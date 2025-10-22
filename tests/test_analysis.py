import pytest
import pandas as pd
import numpy as np
from main import (
    preprocess_data, 
    detect_outliers_iqr, 
    detect_outliers_zscore,
    calculate_statistics,
    get_status
)

# ========== テストデータ生成 ==========

def create_test_dataframe():
    """テスト用のDataFrameを作成"""
    np.random.seed(42)
    data = {
        "zone_name": ["A_Assemble"] * 100 + ["B_Assemble"] * 100,
        "adjusted_time_seconds": list(np.random.normal(5.0, 0.5, 100)) + 
                                 list(np.random.normal(7.0, 1.0, 100)),
        "cycle_number": range(200),
        "is_outlier": [False] * 200
    }
    df = pd.DataFrame(data)
    
    # 意図的に異常値を追加
    df.loc[10, "adjusted_time_seconds"] = 15.0  # 明確な外れ値
    df.loc[110, "adjusted_time_seconds"] = 15.0  # 明確な外れ値
    
    return df

# ========== 前処理テスト ==========

def test_preprocess_valid_data():
    """正常なデータの前処理テスト"""
    df = create_test_dataframe()
    df_clean, stats, error = preprocess_data(df)
    
    assert error is None
    assert df_clean is not None
    assert len(df_clean) > 0
    assert stats["removed_missing"] == 0
    assert stats["removed_invalid"] == 0

def test_preprocess_with_nan():
    """欠損値を含むデータの前処理テスト"""
    df = create_test_dataframe()
    df.loc[0, "adjusted_time_seconds"] = np.nan
    df.loc[1, "zone_name"] = np.nan
    
    df_clean, stats, error = preprocess_data(df)
    
    assert error is None
    assert stats["removed_missing"] == 2
    assert len(df_clean) == 198

def test_preprocess_with_invalid_values():
    """無効値を含むデータの前処理テスト"""
    df = create_test_dataframe()
    df.loc[0, "adjusted_time_seconds"] = -1.0
    df.loc[1, "adjusted_time_seconds"] = 0.0
    
    df_clean, stats, error = preprocess_data(df)
    
    assert error is None
    assert stats["removed_invalid"] == 2
    assert len(df_clean) == 198

def test_preprocess_missing_columns():
    """必須列が欠けている場合のテスト"""
    df = pd.DataFrame({"wrong_column": [1, 2, 3]})
    df_clean, stats, error = preprocess_data(df)
    
    assert df_clean is None
    assert error is not None

# ========== 異常値検出テスト ==========

def test_detect_outliers_iqr():
    """IQR法による異常値検出テスト"""
    # 正規分布 + 外れ値
    data = pd.Series([5.0] * 90 + [15.0] * 10)
    outliers = detect_outliers_iqr(data)
    
    assert outliers.sum() >= 10  # 最低10個の外れ値が検出される
    assert outliers[90] == True  # 15.0は外れ値

def test_detect_outliers_zscore():
    """Z-score法による異常値検出テスト"""
    # 平均5.0、標準偏差1.0で、15.0は明らかに外れ値
    data = pd.Series([5.0] * 90 + [15.0] * 10)
    outliers = detect_outliers_zscore(data)
    
    assert outliers.sum() > 0  # 外れ値が検出される
    assert outliers[90] == True  # 15.0は外れ値

def test_detect_outliers_zscore_zero_std():
    """標準偏差がゼロの場合のテスト"""
    data = pd.Series([5.0] * 100)  # すべて同じ値
    outliers = detect_outliers_zscore(data)
    
    assert outliers.sum() == 0  # 外れ値なし

# ========== 統計計算テスト ==========

def test_calculate_statistics():
    """統計計算のテスト"""
    df = create_test_dataframe()
    target_values = {"A_Assemble": 5.0, "B_Assemble": 7.0}
    
    stats = calculate_statistics(df, target_values)
    
    assert "A_Assemble" in stats
    assert "B_Assemble" in stats
    assert stats["A_Assemble"]["target"] == 5.0
    assert stats["A_Assemble"]["count"] == 100
    assert "mean" in stats["A_Assemble"]
    assert "min" in stats["A_Assemble"]
    assert "max" in stats["A_Assemble"]
    assert "achieve_rate" in stats["A_Assemble"]

def test_get_status():
    """ステータス判定のテスト"""
    assert get_status(95, 90, 70) == "○"
    assert get_status(85, 90, 70) == "△"
    assert get_status(65, 90, 70) == "×"
    assert get_status(90, 90, 70) == "○"  # 境界値
    assert get_status(70, 90, 70) == "△"  # 境界値

# ========== 実行 ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v"])