#!/usr/bin/env python3

import argparse
import os
import time
import uuid

import jwt

JWT_ALGORITHM = "HS256"


def generate_token(agent_id: str, models: list, days: int, secret: str) -> str:
    now = int(time.time())
    payload = {
        "sub": agent_id,          
        "models": models,       
        "iat": now,
        "exp": now + days * 86400,
        "jti": str(uuid.uuid4()), 
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def main():
    parser = argparse.ArgumentParser(description="Generate a scoped token for an ADK agent")
    parser.add_argument("--agent-id", required=True, help="Unique identifier for the agent (shows up in proxy logs)")
    parser.add_argument("--models", nargs="+", required=True, help="Model names this agent may call")
    parser.add_argument("--days", type=int, default=60, help="Token validity in days (default: 60)")
    parser.add_argument("--output-file", help="Write the token here instead of stdout")
    args = parser.parse_args()

    secret = os.environ.get("LITELLM_PROXY_JWT_SECRET")
    if not secret:
        raise SystemExit("LITELLM_PROXY_JWT_SECRET env var must be set (same secret the proxy verifies against)")

    token = generate_token(args.agent_id, args.models, args.days, secret)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"token={token}\n")
    elif args.output_file:
        with open(args.output_file, "w") as f:
            f.write(token)
        os.chmod(args.output_file, 0o600)
    else:
        raise SystemExit(
            "No GITHUB_OUTPUT detected and no --output-file given — "
            "refusing to print the token. Pass --output-file <path> for local use."
        )


if __name__ == "__main__":
    main()