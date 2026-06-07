from fastapi import HTTPException, status

invalid_creds_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)
