import pytest
from backend.utils.auth_util import create_access_token, decode_token
from fastapi import HTTPException


def test_create_and_decode_token():
    token = create_access_token({"sub": "alice"})
    assert decode_token(token) == "alice"


def test_decode_invalid_token_raises():
    with pytest.raises(HTTPException):
        decode_token("not-a-valid-token")
