import os
import sys
import requests


LITELLM_PROXY_URL = os.environ["LITELLM_PROXY_URL"]
MASTER_KEY = os.environ["LITELLM_PROXY_MASTER_KEY"]
GOOGLE_ID_TOKEN = os.environ["GOOGLE_ID_TOKEN"]
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
            # LiteLLM authentication
            "Authorization": f"Bearer {MASTER_KEY}",

            # Cloud Run IAM authentication
            "X-Serverless-Authorization": f"Bearer {GOOGLE_ID_TOKEN}",

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
    print(
        f"ERROR: Failed to generate LiteLLM virtual key: {exc}",
        file=sys.stderr,
    )

    if "response" in locals() and response is not None:
        print(
            f"LiteLLM response status: {response.status_code}",
            file=sys.stderr,
        )
        print(
            f"LiteLLM response: {response.text}",
            file=sys.stderr,
        )

    sys.exit(1)


try:
    data = response.json()
except ValueError:
    print(
        "ERROR: LiteLLM returned an invalid JSON response.",
        file=sys.stderr,
    )
    sys.exit(1)


virtual_key = data.get("key")

if not virtual_key:
    print(
        "ERROR: LiteLLM response did not contain a virtual key.",
        file=sys.stderr,
    )
    sys.exit(1)


# Prevent the virtual key from appearing in GitHub Actions logs.
print(f"::add-mask::{virtual_key}")

# Make the virtual key available to subsequent workflow steps.
with open(os.environ["GITHUB_ENV"], "a") as env_file:
    env_file.write(f"LITELLM_VIRTUAL_KEY={virtual_key}\n")

print("LiteLLM virtual key generated successfully.")