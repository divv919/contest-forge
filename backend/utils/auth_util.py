from datetime import datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from ..config import get_settings
from .exceptions import invalid_creds_exc

settings = get_settings()

SECRET_KEY = (
    settings.secret_key or "716ee0a822d92d9b76092660b83a31ef39eacf64066003d84450cea5d35be746"
)

ALGORITHM = settings.algorithm
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=15)
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise invalid_creds_exc
        return username
    except InvalidTokenError:
        raise invalid_creds_exc from None
