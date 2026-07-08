FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ★ここが一番重要です！本番環境用の最強起動コマンド
CMD gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 60 gem:app
