"""
UI表示モジュール
Streamlitのウィジェットと画面表示を担当
"""

import os
import streamlit as st
import pandas as pd
from constants import ICON_PATH
from data_processing import get_status
from visualizations import plot_histograms, plot_timeseries


def display_preprocess_stats(preprocess_stats):
    """前処理統計を表示"""
    with st.expander("📊 データ前処理情報", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("元データ行数", preprocess_stats["original_rows"])
        col2.metric("欠損値除外", preprocess_stats["removed_missing"])
        col3.metric("無効値除外", preprocess_stats["removed_invalid"])
        col4.metric("処理後行数", preprocess_stats["final_rows"])


def display_statistics_table(stats_dict, threshold_good, threshold_ok):
    """統計表を表示"""
    stats_df = pd.DataFrame(stats_dict).T
    stats_df["status"] = stats_df["achieve_rate"].apply(
        lambda x: get_status(x, threshold_good, threshold_ok)
    )
    stats_df = stats_df[["target", "mean", "min", "max", "achieve_rate", "status", "count"]]
    stats_df.columns = ["目標", "平均", "最小", "最大", "達成率(%)", "ステータス", "データ数"]
    
    st.dataframe(stats_df, use_container_width=True)


def display_histograms(df_clean, target_values, bins):
    """ヒストグラムを表示"""
    fig = plot_histograms(df_clean, target_values, bins=bins)
    st.plotly_chart(fig, use_container_width=True)


def display_timeseries(df_clean, target_values, show_ma, ma_window):
    """時系列グラフを表示"""
    fig = plot_timeseries(df_clean, target_values, show_ma=show_ma, ma_window=ma_window)
    st.plotly_chart(fig, use_container_width=True)


def display_outliers_list(df_clean):
    """異常値リストを表示"""
    st.subheader("🚨 検出された異常値")
    
    # 信頼度別に分類
    high_conf = df_clean[df_clean["iqr_flag"] & df_clean["zscore_flag"]]
    low_conf = df_clean[(df_clean["iqr_flag"] | df_clean["zscore_flag"]) & 
                       ~(df_clean["iqr_flag"] & df_clean["zscore_flag"])]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("高信頼異常値", len(high_conf))
    with col2:
        st.metric("低信頼異常値", len(low_conf))
    
    # タブで分類表示
    tab1, tab2 = st.tabs(["高信頼異常値", "低信頼異常値"])
    
    with tab1:
        if len(high_conf) > 0:
            display_cols = ["zone_name", "adjusted_time_seconds", "iqr_flag", "zscore_flag"]
            if "is_outlier" in high_conf.columns:
                display_cols.append("is_outlier")
            st.dataframe(high_conf[display_cols].head(50), use_container_width=True)
        else:
            st.info("高信頼異常値は検出されませんでした")
    
    with tab2:
        if len(low_conf) > 0:
            display_cols = ["zone_name", "adjusted_time_seconds", "iqr_flag", "zscore_flag"]
            if "is_outlier" in low_conf.columns:
                display_cols.append("is_outlier")
            st.dataframe(low_conf[display_cols].head(50), use_container_width=True)
        else:
            st.info("低信頼異常値は検出されませんでした")


def display_llm_analysis(client, llm_json, analyze_with_llm_func):
    """LLM分析結果を表示"""
    st.header("🤖 AI分析結果")
    
    # LLM分析実行
    if client and st.session_state.llm_response is None:
        col1, col2 = st.columns([2, 15])
        with col1:
            # カスタムアイコンを表示（大きく）
            if os.path.exists(ICON_PATH):
                st.image(ICON_PATH, width=120)
            else:
                st.markdown("🤖")  # フォールバック
        with col2:
            # 全角2文字分の余白を追加
            st.markdown('<div style="padding-left: 2em;">', unsafe_allow_html=True)
            stream_placeholder = st.empty()
            with st.spinner("AIが分析中..."):
                llm_response, llm_error = analyze_with_llm_func(
                    client, llm_json, stream_placeholder
                )
                
                if llm_error:
                    st.error(llm_error)
                else:
                    st.session_state.llm_response = llm_response
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.llm_response:
        col1, col2 = st.columns([2, 15])
        with col1:
            # カスタムアイコンを表示（大きく）
            if os.path.exists(ICON_PATH):
                st.image(ICON_PATH, width=120)
            else:
                st.markdown("🤖")  # フォールバック
        with col2:
            # 全角2文字分の余白を追加してテキストを表示
            st.markdown(f'<div style="padding-left: 2em;">{st.session_state.llm_response}</div>', 
                       unsafe_allow_html=True)
    
    elif not client:
        st.warning("⚠️ OpenAI APIキーが設定されていないため、AI分析を実行できません")