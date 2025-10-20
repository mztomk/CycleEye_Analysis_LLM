# 製造ラインデータ可視化・解析システム

製造ラインの4ゾーン（A_Assemble, A2_Assemble, B_Assemble, B2_Assemble）のサイクルタイムデータを# 製造ラインデータ可視化・解析システム

製造ラインの4ゾーン（A_Assemble, A2_Assemble, B_Assemble, B2_Assemble）のサイクルタイムデータを可視化・解析し、**OpenAI GPT-4oによるAI分析**を提供するStreamlitアプリケーションです。

## 主な機能

- **データ前処理**: 欠損値・無効値の自動除外
- **異常値検出**: IQR法とZ-score法による冗長判定
- **統計分析**: ゾーン別の達成率、平均、最小/最大、標準偏差の計算
- **可視化**: 
  - 統計表
  - ヒストグラム（全ゾーン統一スケール）
  - 時系列グラフ（移動平均オプション付き）
  - 異常値リスト（信頼度別表示）
- **🤖 AI分析（NEW!）**: 
  - OpenAI GPT-4oによる自動分析
  - ストリーミング表示でリアルタイムに結果表示
  - 問題点の指摘と具体的な改善提案
  - ワンクリックで「グラフ作成→AI分析」まで完結
- **LLM向けJSON出力**: 構造化されたデータをJSON形式でエクスポート

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <your-repo-url>
cd manufacturing-line-analysis
```

### 2. 仮想環境の作成（推奨）

```bash
python3 -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. OpenAI APIキーの設定

#### ローカル環境の場合

1. `.env.sample` を `.env` にコピー
```bash
cp .env.sample .env
```

2. `.env` ファイルを編集してAPIキーを設定
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. `.gitignore` に `.env` を追加（セキュリティのため）
```bash
echo ".env" >> .gitignore
```

#### Streamlit Cloudの場合

Streamlit Cloudのダッシュボードで以下のように設定：

1. アプリの Settings → Secrets をクリック
2. 以下を追加：
```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

### 5. CSVファイルの配置

デフォルトのCSVファイル `generated_cycles_4zones_2000rows.csv` をプロジェクトルートに配置してください。

## 実行方法

### ローカル実行

```bash
streamlit run main.py
```

ブラウザが自動で開き、`http://localhost:8501` でアプリケーションが表示されます。

### テストの実行

```bash
pytest test_analysis.py -v
```

## 使用方法

### 1. データ読み込み

- **デフォルト**: サイドバーの「CSVパス」欄に指定されたファイルが自動読み込み
- **ファイルアップロード**: サイドバーの「CSVファイルをアップロード」から手動アップロード可能
- **サンプリング**: 大規模データの場合、「サンプリング行数」で最新n行のみ処理可能

### 2. ターゲット設定

サイドバーの「🎯 ターゲット設定」で各ゾーンの目標サイクルタイム（秒）を設定します。

### 3. ステータス閾値調整

- **○ (良好)**: 達成率がこの値以上
- **△ (注意)**: 達成率がこの値以上、○の閾値未満
- **× (要改善)**: 達成率がこの値未満

### 4. 🚀 分析を実行

サイドバー下部の **「🚀 分析を実行」ボタン** をクリックすると、以下が自動で実行されます：

1. データの前処理（欠損値・異常値除外）
2. 統計計算と異常値検出
3. グラフの作成
4. **GPT-4oによるAI分析（ストリーミング表示）**

### 5. グラフ表示

ラジオボタンで以下の表示を切り替え：

- **統計表**: 各ゾーンの統計サマリー
- **ヒストグラム**: 分布の可視化（ビン数調整可能）
- **時系列グラフ**: サイクルタイムの推移（移動平均オプション付き）
- **異常値リスト**: 高信頼/低信頼異常値の一覧

### 6. AI分析結果の確認

画面下部の **「🤖 AI分析結果」セクション** に以下が表示されます：

- 🤖 ロボットアイコン（後でカスタム画像に変更可能）
- リアルタイムストリーミング表示で分析結果が表示
- 各ゾーンの評価、問題点、改善提案を含む

### 7. JSON出力とダウンロード

- **分析データ**: LLMが解析可能な構造化データ
- **JSONダウンロード**: ボタンクリックでローカル保存

### 8. ログ保存

サイドバーの「💾 分析ログを保存」ボタンで、分析設定とタイムスタンプを `analysis_logs.json` に記録します。

## ファイル構成

```
.
├── main.py                                    # メインアプリケーション
├── test_analysis.py                           # ユニットテスト
├── requirements.txt                           # 依存パッケージ
├── .env.sample                                # 環境変数サンプル
├── .env                                       # 環境変数（要作成、.gitignore推奨）
├── README.md                                  # このファイル
├── generated_cycles_4zones_2000rows.csv       # サンプルデータ
├── analysis_logs.json                         # 分析ログ（自動生成）
└── assets/                                    # 将来的なカスタムアイコン用（オプション）
    └── robot_icon.png                         # カスタムロボットアイコン
```

## CSV仕様

### 必須列

- `zone_name`: ゾーン名（A_Assemble, A2_Assemble, B_Assemble, B2_Assemble）
- `adjusted_time_seconds`: 調整済みサイクルタイム（秒）

### オプション列

- `cycle_number`: サイクル番号
- `start_datetime` / `end_datetime`: タイムスタンプ
- `start_frame` / `end_frame`: フレーム番号
- `elapsed_seconds`: 経過秒数
- `is_outlier`: 既存の異常値フラグ（比較用）
- `created_at`: 作成日時

## 異常値検出ロジック

### IQR法

```
Q1 = 第1四分位数
Q3 = 第3四分位数
IQR = Q3 - Q1
下限 = Q1 - 1.5 × IQR
上限 = Q3 + 1.5 × IQR
```

値が下限未満または上限超の場合、`iqr_flag=True`

### Z-score法

```
z = (x - mean) / std
```

|z| > 3 の場合、`zscore_flag=True`

### 信頼度判定

- **高信頼異常値**: `iqr_flag=True` かつ `zscore_flag=True`
- **低信頼異常値**: いずれか一方のみ `True`

## Streamlit Cloudへのデプロイ

### 1. GitHubリポジトリにプッシュ

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud) にログイン
2. 「New app」をクリック
3. リポジトリ、ブランチ、main.pyを選択
4. 「Deploy!」をクリック

### 3. Secrets設定（LLM API使用時）

Settings → Secrets で以下のように設定：

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

## カスタムアイコンの設定方法

デフォルトでは絵文字の🤖が表示されますが、カスタム画像に変更できます：

### 1. アイコン画像の準備

1. プロジェクトルートに `assets` フォルダを作成
2. ロボットアイコン画像（PNG推奨）を配置: `assets/robot_icon.png`

### 2. コードの修正

`main.py` の該当箇所を以下のように変更：

```python
# 変更前
with col1:
    st.markdown("🤖")

# 変更後
with col1:
    st.image("assets/robot_icon.png", width=50)
```

### 3. Streamlit Cloudへのデプロイ

`assets` フォルダごとGitHubにプッシュすれば自動反映されます。

## API使用料金について

### OpenAI GPT-4o料金（2024年時点）

- **入力**: $5.00 / 1M tokens
- **出力**: $15.00 / 1M tokens

### 概算コスト（1回の分析あたり）

- 入力トークン: 約1,000〜2,000トークン（$0.005〜$0.01）
- 出力トークン: 約500〜1,000トークン（$0.0075〜$0.015）
- **合計**: 約 $0.01〜$0.03 / 回

月間100回の分析で約$1〜$3程度です。

## セキュリティに関する注意

### APIキーの管理

- ⚠️ **絶対にGitHubにAPIキーをコミットしないでください**
- `.env` ファイルは必ず `.gitignore` に追加
- Streamlit CloudではSecretsを使用

### .gitignore に追加すべきファイル

```
.env
*.pyc
__pycache__/
analysis_logs.json
*.log
```

## トラブルシューティング

### エラー: "APIキーが設定されていません"

**原因**: OpenAI APIキーが正しく設定されていない

**解決方法**:
- ローカル: `.env` ファイルに `OPENAI_API_KEY=sk-xxx` を記載
- Streamlit Cloud: Settings → Secrets に `OPENAI_API_KEY = "sk-xxx"` を追加
- APIキーの取得: [OpenAI Platform](https://platform.openai.com/api-keys)

### エラー: "必須列が不足しています"

CSVに `zone_name` と `adjusted_time_seconds` 列が含まれているか確認してください。

### エラー: "データ読み込みエラー"

- CSVファイルのパスが正しいか確認
- ファイルのエンコーディングがUTF-8か確認
- ファイルの読み取り権限を確認

### グラフが表示されない

- データが正常に読み込まれているか「データ前処理情報」を確認
- 「🚀 分析を実行」ボタンをクリックしたか確認
- ブラウザのキャッシュをクリアしてリロード

### AI分析が実行されない

- OpenAI APIキーが正しく設定されているか確認
- APIキーに十分なクレジットがあるか確認
- インターネット接続を確認

### ストリーミング表示が途中で止まる

- OpenAIのサーバー状態を確認: [status.openai.com](https://status.openai.com/)
- API レート制限に達していないか確認
- ページをリロードして再実行

### テストが失敗する

```bash
# 依存関係を再インストール
pip install -r requirements.txt --upgrade

# テストを再実行
pytest test_analysis.py -v
```

## パフォーマンス最適化

### 大規模データの処理

- サンプリング機能を使用（例: 最新10,000行）
- Streamlitのキャッシュ機能により2回目以降は高速化

### メモリ使用量の削減

- 不要な列を事前に削除
- データ型を最適化（float64 → float32など）

## 今後の拡張予定

- [ ] リアルタイムデータ連携
- [x] **OpenAI GPT-4o統合（完了）**
- [x] **ストリーミング表示（完了）**
- [ ] カスタムアイコン画像対応
- [ ] Claude API対応
- [ ] 多言語対応（英語、中国語）
- [ ] PDF/Excelレポート自動生成
- [ ] 作業者別・設備別の分析機能
- [ ] 予測モデル（次サイクルの予測）
- [ ] 音声入力による分析リクエスト

## ライセンス

MIT License

## 開発者

製造ラインデータ解析チーム

## お問い合わせ

バグ報告や機能要望は、GitHubのIssuesにてお願いします。