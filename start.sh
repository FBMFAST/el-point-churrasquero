#!/bin/sh
set -e

streamlit run app.py \
    --server.port=8501 \
    --server.address=127.0.0.1 \
    --server.enableStaticServing=true &

envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/sites-available/default

nginx -g "daemon off;"