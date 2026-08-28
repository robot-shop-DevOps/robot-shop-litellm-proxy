FROM asia-south1-docker.pkg.dev/robotshop-platform-dev/baseimages/python:3.14.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY config/litellm_proxy.yaml ./config/litellm_proxy.yaml

EXPOSE 4000

CMD ["litellm", "--config", "/app/config/litellm_proxy.yaml"]