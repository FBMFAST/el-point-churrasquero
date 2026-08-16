FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY . /app 

RUN pip install --no-cache-dir -r requirements.txt

RUN sed -i 's/\r$//' /app/start.sh /app/nginx.conf.template \
    && chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
