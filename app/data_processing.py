"""
データ処理モジュール
CSV読み込み、前処理、異常値検出、統計計算を担当
"""

import pandas as pd
import numpy as np
import streamlit as st
from constants import ZONES, DEFAULT_TARGET


@st.cache_data
def load_csv_data(file_path):
    """CSVデータを読み込む"""
    try:
        df = pd.read_csv(file_path)
        return df, None
    except Exception as e:
        return None, str(e)


@st.cache_data
def preprocess_data(df):
    """データ前処理"""
    stats_log = {
        "original_rows": len(df),
        "removed_missing": 0,
        "removed_invalid": 0
    }
    
    # 必須列チェック
    required_cols = ["zone_name", "adjusted_time_seconds"]
    if not all(col in df.columns for col in required_cols):
        return None, stats_log, "必須列が不足しています"
    
    # 欠損値除外
    original_len = len(df)
    df = df.dropna(subset=["adjusted_time_seconds", "zone_name"])
    stats_log["removed_missing"] = original_len - len(df)
    
    # 無効値除外 (adjusted_time_seconds <= 0)
    original_len = len(df)
    df = df[df["adjusted_time_seconds"] > 0]
    stats_log["removed_invalid"] = original_len - len(df)
    
    stats_log["final_rows"] = len(df)
    
    return df, stats_log, None


def detect_outliers_iqr(series):
    """IQR法による異常値検出"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (series < lower_bound) | (series > upper_bound)


def detect_outliers_zscore(series):
    """Z-score法による異常値検出"""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.Series([False] * len(series), index=series.index)
    z_scores = np.abs((series - mean) / std)
    return z_scores > 3


@st.cache_data
def analyze_outliers(df):
    """ゾーン別に異常値を検出"""
    df = df.copy()
    df["iqr_flag"] = False
    df["zscore_flag"] = False
    
    for zone in ZONES:
        zone_mask = df["zone_name"] == zone
        if zone_mask.sum() > 0:
            zone_data = df.loc[zone_mask, "adjusted_time_seconds"]
            df.loc[zone_mask, "iqr_flag"] = detect_outliers_iqr(zone_data)
            df.loc[zone_mask, "zscore_flag"] = detect_outliers_zscore(zone_data)
    
    return df


@st.cache_data
def calculate_statistics(df, target_values):
    """ゾーン別統計を計算"""
    stats_dict = {}
    
    for zone in ZONES:
        zone_data = df[df["zone_name"] == zone]["adjusted_time_seconds"]
        if len(zone_data) == 0:
            continue
        
        target = target_values.get(zone, DEFAULT_TARGET)
        mean_val = zone_data.mean()
        achieve_rate = (target / mean_val * 100) if mean_val > 0 else 0
        
        stats_dict[zone] = {
            "target": round(target, 1),
            "mean": round(mean_val, 1),
            "min": round(zone_data.min(), 1),
            "max": round(zone_data.max(), 1),
            "std": round(zone_data.std(), 1),
            "achieve_rate": round(achieve_rate, 1),
            "count": len(zone_data)
        }
    
    return stats_dict


def get_status(achieve_rate, threshold_good, threshold_ok):
    """達成率からステータスを判定"""
    if achieve_rate >= threshold_good:
        return "○"
    elif achieve_rate >= threshold_ok:
        return "△"
    else:
        return "×"