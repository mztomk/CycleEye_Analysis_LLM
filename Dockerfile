FROM python:3.10-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt をコピー
COPY app/requirements.txt .

# Pythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ .
COPY data/ ./data/
COPY assets/ ./assets/

# Streamlit用ポート
EXPOSE 8501

# Streamlit実行
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0"]