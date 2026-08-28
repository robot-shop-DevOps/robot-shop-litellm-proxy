import os
import requests


LITELLM_URL = os.environ["LITELLM_URL"]
MASTER_KEY = os.environ["LITELLM_MASTER_KEY"]

agent = os.environ["AGENT"]
models = os.environ["MODELS"].split()


response = requests.post(
    f"{LITELLM_URL}/key/generate",
    headers={
        "Authorization": f"Bearer {MASTER_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "key_alias": agent,
        "models": models,
    },
)

response.raise_for_status()

data = response.json()

print(data)