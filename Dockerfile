FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python scripts/gen_keywords.py && python scripts/ingest.py

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]