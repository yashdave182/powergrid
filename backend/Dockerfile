FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

# Use shell form so runtime environment variables like $PORT are expanded by the shell
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# Optional simple healthcheck (can be used by platforms that support Docker HEALTHCHECK)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1