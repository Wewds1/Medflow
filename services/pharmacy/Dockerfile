FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default to API. Consumer can be overridden in docker-compose.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
