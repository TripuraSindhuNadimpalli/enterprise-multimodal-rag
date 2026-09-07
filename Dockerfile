FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch to avoid downloading large CUDA packages.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.13.0 \
    && pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY auth ./auth
COPY config ./config
COPY database ./database
COPY ingestion ./ingestion
COPY monitoring ./monitoring
COPY retrieval ./retrieval
COPY storage ./storage
COPY workers ./workers

EXPOSE 8000

CMD ["sh", "-c", "python -m database.init_db && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
