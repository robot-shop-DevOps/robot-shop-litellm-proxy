import os
import sys
import requests


LITELLM_PROXY_URL = os.environ["LITELLM_PROXY_URL"]
MASTER_KEY = os.environ["LITELLM_PROXY_MASTER_KEY"]
AGENT = os.environ["AGENT"]
MODELS = os.environ["MODELS"].split()


print("Starting LiteLLM virtual key generation...")
print(f"Agent: {AGENT}")
print(f"Models: {', '.join(MODELS)}")
print(f"LiteLLM URL: {LITELLM_PROXY_URL}")

try:
    response = requests.post(
        f"{LITELLM_PROXY_URL}/key/generate",
        headers={
            "Authorization": f"Bearer {MASTER_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "key_alias": AGENT,
            "models": MODELS,
        },
        timeout=30,
    )

    response.raise_for_status()

except requests.RequestException as exc:
    print(f"ERROR: Failed to generate LiteLLM virtual key: {exc}", file=sys.stderr)

    if response is not None:
        print(
            f"LiteLLM response status: {response.status_code}",
            file=sys.stderr,
        )

    sys.exit(1)


data = response.json()
virtual_key = data.get("key")

if not virtual_key:
    print("ERROR: LiteLLM response did not contain a virtual key.", file=sys.stderr)
    sys.exit(1)

print(f"::add-mask::{virtual_key}")

with open(os.environ["GITHUB_ENV"], "a") as env_file:
    env_file.write(f"LITELLM_VIRTUAL_KEY={virtual_key}\n")

print("LiteLLM virtual key generated successfully.")