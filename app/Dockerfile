FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
CMD ["sh", "-c", "./wait-for-it.sh postgres alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]