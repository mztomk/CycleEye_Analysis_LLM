"""
定数定義モジュール
アプリケーション全体で使用する定数を管理
"""

# ファイルパス
DEFAULT_CSV_PATH = "generated_cycles_4zones_2000rows.csv"
ICON_PATH = "assets/robot_icon.png"

# ゾーン定義
ZONES = ["A_Assemble", "A2_Assemble", "B_Assemble", "B2_Assemble"]

# デフォルト設定値
DEFAULT_TARGET = 5.0
DEFAULT_THRESHOLD_GOOD = 90
DEFAULT_THRESHOLD_OK = 80
DEFAULT_BINS = 30
DEFAULT_SHOW_MA = False
DEFAULT_MA_WINDOW = 5

# グラフ設定
CHART_HEIGHT = 700
Y_AXIS_RANGE = [4, 12]  # 時系列グラフのY軸範囲
TARGET_LINE_COLOR = "rgba(255, 100, 100, 0.6)"  # 薄い赤色
TARGET_LINE_WIDTH = 2

# LLM設定
LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000

# ログ設定
LOG_FILE_PATH = "analysis_logs.json"
PROMPT_VERSION = "v1.0.0"