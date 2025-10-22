"""
グラフ描画モジュール
ヒストグラム、時系列グラフの描画を担当
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from constants import (
    ZONES, DEFAULT_TARGET, CHART_HEIGHT, Y_AXIS_RANGE,
    TARGET_LINE_COLOR, TARGET_LINE_WIDTH
)


def plot_histograms(df, target_values, bins=30):
    """4ゾーンのヒストグラムを描画（目標線付き）"""
    # 全体の範囲計算（10%マージン）
    overall_min = df["adjusted_time_seconds"].min()
    overall_max = df["adjusted_time_seconds"].max()
    margin = (overall_max - overall_min) * 0.1
    x_range = [overall_min - margin, overall_max + margin]
    
    fig = make_subplots(rows=2, cols=2, 
                        subplot_titles=ZONES,
                        vertical_spacing=0.20,  # 上下の間隔を広く
                        horizontal_spacing=0.1)
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    
    for idx, zone in enumerate(ZONES):
        row, col = positions[idx]
        zone_data = df[df["zone_name"] == zone]["adjusted_time_seconds"]
        target = target_values.get(zone, DEFAULT_TARGET)
        
        # ヒストグラム
        fig.add_trace(
            go.Histogram(x=zone_data, nbinsx=bins, name=zone,
                        marker_color='steelblue'),
            row=row, col=col
        )
        
        # 目標値の線を追加
        fig.add_vline(
            x=target, 
            line_dash="dash", 
            line_color=TARGET_LINE_COLOR,
            line_width=TARGET_LINE_WIDTH,
            annotation_text=f"目標: {target}秒",
            annotation_position="top",
            row=row, col=col
        )
        
        fig.update_xaxes(range=x_range, title_text="組立時間 (秒)", row=row, col=col)
        fig.update_yaxes(title_text="サイクル数", row=row, col=col)
    
    fig.update_layout(
        height=CHART_HEIGHT,
        showlegend=False,
        title_text="ヒストグラム"
    )
    return fig


def plot_timeseries(df, target_values, show_ma=False, ma_window=5):
    """4ゾーンの時系列グラフを描画（縦軸4~12秒統一 + 目標線）"""
    fig = make_subplots(rows=2, cols=2, 
                        subplot_titles=ZONES,
                        vertical_spacing=0.20,  # 上下の間隔を広く
                        horizontal_spacing=0.1)
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    
    for idx, zone in enumerate(ZONES):
        row, col = positions[idx]
        zone_df = df[df["zone_name"] == zone].sort_index()
        target = target_values.get(zone, DEFAULT_TARGET)
        
        # X軸: timestampがあればそれを、なければindex
        if "start_datetime" in zone_df.columns:
            try:
                x_data = pd.to_datetime(zone_df["start_datetime"])
            except:
                x_data = zone_df.index
        else:
            x_data = zone_df.index
        
        y_data = zone_df["adjusted_time_seconds"]
        
        # データプロット
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, mode='lines+markers',
                      name=zone, line=dict(color='steelblue', width=1),
                      marker=dict(size=3)),
            row=row, col=col
        )
        
        # 目標値の水平線を追加
        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color=TARGET_LINE_COLOR,
            line_width=TARGET_LINE_WIDTH,
            annotation_text=f"目標: {target}秒",
            annotation_position="right",
            row=row, col=col
        )
        
        # 移動平均
        if show_ma and len(y_data) >= ma_window:
            ma = y_data.rolling(window=ma_window, center=True).mean()
            fig.add_trace(
                go.Scatter(x=x_data, y=ma, mode='lines',
                          name=f'{zone}_MA{ma_window}',
                          line=dict(color='orange', width=2, dash='dash')),
                row=row, col=col
            )
        
        fig.update_xaxes(title_text="時刻", row=row, col=col)
        fig.update_yaxes(range=Y_AXIS_RANGE, title_text="組立時間 (秒)", row=row, col=col)
    
    fig.update_layout(
        height=CHART_HEIGHT,
        showlegend=False,
        title_text="時系列グラフ"
    )
    return fig