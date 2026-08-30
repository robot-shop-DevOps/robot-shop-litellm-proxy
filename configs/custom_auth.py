import os
import jwt
from fastapi import Request
from litellm.proxy._types import UserAPIKeyAuth

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ["LITELLM_PROXY_JWT_SECRET"] 


async def user_api_key_auth(request: Request, api_key: str) -> UserAPIKeyAuth:
    token = _strip_bearer(api_key)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

    agent_id = payload.get("sub")
    allowed_models = payload.get("models") or []

    if not agent_id or not allowed_models:
        raise Exception("Token missing required claims (sub / models)")

    requested_model = await _get_requested_model(request)
    if requested_model and requested_model not in allowed_models:
        raise Exception(
            f"Agent '{agent_id}' is not permitted to use model '{requested_model}'"
        )

    return UserAPIKeyAuth(
        api_key=token,
        user_id=agent_id,
        models=allowed_models,
        metadata={"agent_id": agent_id, "jti": payload.get("jti")},
    )


def _strip_bearer(api_key: str) -> str:
    if not api_key:
        raise Exception("No token provided")
    return api_key[7:].strip() if api_key.lower().startswith("bearer ") else api_key.strip()


async def _get_requested_model(request: Request):
    try:
        body = await request.json()
        return body.get("model")
    except Exception:
        return None