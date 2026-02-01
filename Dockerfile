FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use PORT environment variable typically set by Cloud Run (default 8080)
ENV PORT=8080

CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
