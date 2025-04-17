FROM python:3

WORKDIR /app

COPY app.py .
COPY anomaly.yaml .
COPY requirements.txt .
COPY anomaly_config.yml .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]



