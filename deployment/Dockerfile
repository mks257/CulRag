# CulRAG backend image (FastAPI + Chroma). Build from the repo root:
#   docker build -f deployment/Dockerfile -t culrag-api .
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/sample_foods.csv data/sample_foods.csv

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
