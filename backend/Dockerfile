FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
   openssl \
   ca-certificates \
   && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /app/certs


RUN echo -n | openssl s_client -connect gigachat.devices.sberbank.ru:443 \
   -servername gigachat.devices.sberbank.ru -showcerts 2>/dev/null | \
   awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' > /app/certs/gigachat_query_ssl.pem && \
   [ -s /app/certs/gigachat_query_ssl.pem ] || echo "WARNING: gigachat_query_ssl.pem is empty"


ENV GIGACHAT_QUERY_CERT_PATH=/app/certs/gigachat_query_ssl.pem


RUN echo -n | openssl s_client -connect ngw.devices.sberbank.ru:9443 \
   -servername ngw.devices.sberbank.ru -showcerts 2>/dev/null | \
   awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' > /app/certs/gigachat_ssl.pem && \
   [ -s /app/certs/gigachat_ssl.pem ] || echo "WARNING: gigachat_ssl.pem is empty"


ENV GIGACHAT_AUTH_CERT_PATH=/app/certs/gigachat_ssl.pem


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY backend ./backend


WORKDIR /app/backend
EXPOSE 8000


CMD python appendAvailablesParsers.py && \
   python initRdfRepository.py && \
   uvicorn main:app --host 0.0.0.0 --port 8000