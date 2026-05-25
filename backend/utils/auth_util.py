from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
import os
from fastapi.security import OAuth2PasswordBearer
from .exeptions import invalid_creds_exc

SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM" ,"HS256")

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=15)
    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token : str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise invalid_creds_exc
        return username
    except InvalidTokenError:
        raise invalid_creds_exc
    
