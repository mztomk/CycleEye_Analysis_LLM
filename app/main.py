"""
製造ラインデータ可視化・解析システム - メインアプリケーション
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# モジュールインポート
from constants import (
    DEFAULT_CSV_PATH, ZONES, DEFAULT_TARGET,
    DEFAULT_THRESHOLD_GOOD, DEFAULT_THRESHOLD_OK,
    DEFAULT_BINS, DEFAULT_SHOW_MA, DEFAULT_MA_WINDOW,
    LOG_FILE_PATH, PROMPT_VERSION
)
from data_processing import (
    load_csv_data, preprocess_data, analyze_outliers, calculate_statistics
)
from llm_handler import init_openai_client, generate_llm_json, analyze_with_llm
from ui_components import (
    display_preprocess_stats, display_statistics_table,
    display_histograms, display_timeseries, display_outliers_list,
    display_llm_analysis
)

# ページ設定
st.set_page_config(
    page_title="製造ラインデータ解析",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)


def main():
    st.title("CycleEye -製造ラインデータ可視化・解析システム-")
    
    # OpenAIクライアント初期化
    client, client_error = init_openai_client()
    if client_error:
        st.warning(f"⚠️ {client_error}")
        st.info("💡 .envファイルにOPENAI_API_KEYを設定するか、Streamlit CloudのSecretsに設定してください")
    
    # ========== サイドバー設定 ==========
    st.sidebar.header("⚙️ 設定")
    
    # 目標設定（全ゾーン統一デフォルト5秒）
    st.sidebar.subheader(" 目標タクト設定（秒）")
    target_values = {}
    for zone in ZONES:
        target_values[zone] = st.sidebar.number_input(
            zone, min_value=0.1, value=DEFAULT_TARGET, step=0.1, format="%.1f"
        )
    
    # 分析実行ボタン
    st.sidebar.markdown("---")
    analyze_button = st.sidebar.button("🚀 分析を実行", type="primary", use_container_width=True)
    
    # ========== セッションステートの初期化 ==========
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'llm_response' not in st.session_state:
        st.session_state.llm_response = None
    
    # ========== 分析実行 ==========
    if analyze_button:
        st.session_state.analysis_done = False
        st.session_state.llm_response = None
        
        with st.spinner("データを前処理中..."):
            # データ読み込み
            df, error = load_csv_data(DEFAULT_CSV_PATH)
            
            if error:
                st.error(f"データ読み込みエラー: {error}")
                return
            
            if df is None:
                st.error("CSVファイルが見つかりません")
                return
            
            # 前処理
            df_clean, preprocess_stats, preprocess_error = preprocess_data(df)
            
            if preprocess_error:
                st.error(f"前処理エラー: {preprocess_error}")
                return
            
            # 異常値検出
            df_clean = analyze_outliers(df_clean)
            
            # 統計計算
            stats_dict = calculate_statistics(df_clean, target_values)
            
            # LLM向けJSON生成
            llm_json = generate_llm_json(
                df_clean, stats_dict, DEFAULT_THRESHOLD_GOOD, DEFAULT_THRESHOLD_OK
            )
        
        st.session_state.df_clean = df_clean
        st.session_state.preprocess_stats = preprocess_stats
        st.session_state.stats_dict = stats_dict
        st.session_state.llm_json = llm_json
        st.session_state.target_values = target_values
        st.session_state.analysis_done = True
    
    # ========== 分析結果表示 ==========
    if st.session_state.analysis_done:
        df_clean = st.session_state.df_clean
        preprocess_stats = st.session_state.preprocess_stats
        stats_dict = st.session_state.stats_dict
        llm_json = st.session_state.llm_json
        target_values = st.session_state.target_values
        
        # 前処理統計表示
        display_preprocess_stats(preprocess_stats)
        
        # ========== 4ゾーングラフエリア ==========
        st.header("📊 4ゾーン可視化")
        
        viz_type = st.radio(
            "表示タイプを選択",
            ["統計表", "ヒストグラム", "時系列グラフ", "異常値リスト"],
            horizontal=True
        )
        
        if viz_type == "統計表":
            display_statistics_table(stats_dict, DEFAULT_THRESHOLD_GOOD, DEFAULT_THRESHOLD_OK)
            
        elif viz_type == "ヒストグラム":
            display_histograms(df_clean, target_values, DEFAULT_BINS)
            
        elif viz_type == "時系列グラフ":
            display_timeseries(df_clean, target_values, DEFAULT_SHOW_MA, DEFAULT_MA_WINDOW)
            
        elif viz_type == "異常値リスト":
            display_outliers_list(df_clean)
        
        # ========== LLM分析結果 ==========
        display_llm_analysis(client, llm_json, analyze_with_llm)
        
        # ========== JSON出力 ==========
        st.subheader("📄 JSON出力（LLM向けデータ）")
        with st.expander("JSONを表示", expanded=False):
            st.json(llm_json)
        
        # JSONダウンロード
        json_str = json.dumps(llm_json, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 JSONをダウンロード",
            data=json_str,
            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # ========== ログ保存 ==========
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "csv_file": DEFAULT_CSV_PATH,
            "targets": target_values,
            "prompt_version": PROMPT_VERSION,
            "llm_used": client is not None
        }
        
        # ログをローカル保存
        if st.sidebar.button("💾 分析ログを保存"):
            log_file = Path(LOG_FILE_PATH)
            logs = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            logs.append(log_entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            st.sidebar.success("ログを保存しました")
    
    else:
        st.info("👈 サイドバーの「🚀 分析を実行」ボタンをクリックして分析を開始してください")


if __name__ == "__main__":
    main()