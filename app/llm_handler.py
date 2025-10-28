"""
LLM処理モジュール
OpenAI APIとの連携、JSON生成を担当
"""

import os
import json
import streamlit as st
from openai import OpenAI
from constants import (
    ZONES, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
)
from data_processing import get_status


@st.cache_resource
def init_openai_client():
    """OpenAIクライアントを初期化"""
    try:
        api_key = None
        
        # 環境変数から取得（AWS Lambda/ECS、またはローカルの.envファイル）
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        except Exception:
            pass
        
        # Streamlit Cloudのsecretsから取得
        if not api_key and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
        
        if not api_key:
            return None, "APIキーが設定されていません"
        
        client = OpenAI(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"OpenAIクライアント初期化エラー: {str(e)}"


def generate_llm_json(df, stats_dict, threshold_good, threshold_ok):
    """LLM向けの構造化JSONを生成"""
    output = {
        "summary": {
            "overall_comment": "製造ラインの4ゾーンのサイクルタイムデータを解析しました。"
        },
        "zones": {}
    }
    
    for zone in ZONES:
        if zone not in stats_dict:
            continue
        
        zone_stats = stats_dict[zone]
        zone_data = df[df["zone_name"] == zone]
        
        # 異常値リスト
        anomalies = []
        outlier_data = zone_data[zone_data["iqr_flag"] | zone_data["zscore_flag"]]
        for _, row in outlier_data.head(10).iterrows():
            anomalies.append({
                "timestamp": str(row.get("start_datetime", row.name)),
                "value": float(row["adjusted_time_seconds"]),
                "iqr_flag": bool(row["iqr_flag"]),
                "zscore_flag": bool(row["zscore_flag"])
            })
        
        status = get_status(zone_stats["achieve_rate"], threshold_good, threshold_ok)
        
        # 評価と推奨
        evaluation = f"達成率{zone_stats['achieve_rate']}%（ステータス: {status}）"
        recommendations = []
        
        if zone_stats["achieve_rate"] < threshold_ok:
            recommendations.append({
                "text": f"平均サイクルタイム{zone_stats['mean']}秒がターゲット{zone_stats['target']}秒を大きく上回っています",
                "priority": "High",
                "reason": f"達成率が{zone_stats['achieve_rate']}%と低い"
            })
        
        if zone_stats["std"] > 1.0:
            recommendations.append({
                "text": "ばらつきが大きいため、工程の安定化が必要です",
                "priority": "Medium",
                "reason": f"標準偏差が{zone_stats['std']}秒"
            })
        
        output["zones"][zone] = {
            "stats": {
                "target": zone_stats["target"],
                "mean": zone_stats["mean"],
                "min": zone_stats["min"],
                "max": zone_stats["max"],
                "achieve_rate": zone_stats["achieve_rate"],
                "status": status
            },
            "histogram": {
                "x_min": zone_stats["min"],
                "x_max": zone_stats["max"],
                "bins": 30
            },
            "timeseries": {
                "point_count": zone_stats["count"],
                "notes": "時系列データあり"
            },
            "anomalies": anomalies,
            "evaluation": {
                "short": evaluation
            },
            "recommendations": recommendations
        }
    
    output["requested_additional_data"] = ["作業者情報", "設備保全履歴", "材料ロット情報"]
    
    return output


def analyze_with_llm(client, llm_json, stream_placeholder):
    """OpenAI GPT-4oでデータを分析"""
    
    prompt = f"""
あなたは製造ラインの生産性改善を専門とする熟練のデータアナリストです。
以下のJSONデータは、4つの製造ゾーン（A_Assemble, A2_Assemble, B_Assemble, B2_Assemble）のサイクルタイムデータの統計分析結果です。

**データ概要:**
{json.dumps(llm_json, ensure_ascii=False, indent=2)}

**分析依頼:**
1. 各ゾーンの現状を評価してください（達成率、ばらつき、異常値の観点から）
2. 問題点を優先度順に指摘してください
3. 具体的な改善提案を3-5個提示してください（数値的根拠を含めて）
4. 追加で収集すべきデータがあれば提案してください

**回答形式:**
- 親しみやすく、わかりやすい日本語で回答してください
- 重要な数値は必ず含めてください
- 箇条書きや見出しを使って読みやすくしてください
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "あなたは製造ラインの生産性改善を専門とする熟練のデータアナリストです。"},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                stream_placeholder.markdown(full_response + "▌")
        
        stream_placeholder.markdown(full_response)
        return full_response, None
        
    except Exception as e:
        return None, f"LLM分析エラー: {str(e)}"