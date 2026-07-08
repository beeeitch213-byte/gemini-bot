FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Gunicornを使ってFlaskを安定稼働させる
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "gem:app"]