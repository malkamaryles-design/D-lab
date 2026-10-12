FROM python:3.12-slim
WORKDIR /app

COPY netfree-ca.crt /app/netfree-ca.crt
ENV PIP_CERT=/app/netfree-ca.crt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]