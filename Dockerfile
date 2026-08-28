FROM asia-south1-docker.pkg.dev/robotshop-platform-dev/baseimages/python:3.14.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY configs/litellm_proxy.yaml ./configs/litellm_proxy.yaml

EXPOSE 4000

CMD ["litellm", "--config", "/app/configs/litellm.yaml", "--port", "4000", "--host", "0.0.0.0"]