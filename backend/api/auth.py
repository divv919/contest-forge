from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import  select
from fastapi.security import   OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from ..db.schemas.user import User, UserBase
from ..dependencies.auth_deps import SessionDep, UserDep
from pwdlib import PasswordHash
from ..utils.auth_util import create_access_token
password_hash = PasswordHash.recommended()

router = APIRouter(prefix="/auth", tags=["auth"])

DUMMY_HASH = password_hash.hash("dummy_password")


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token : str
    token_type: str

@router.post("/login")
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    existing_user_statement = select(User).where(User.username == credentials.username)
    existing_user = session.exec(existing_user_statement).first()
    if not existing_user:
        password_hash.verify(credentials.password, DUMMY_HASH)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password", headers={"WWW-Authenticate" : "Bearer"})
    is_password_valid = password_hash.verify(credentials.password, existing_user.password)

    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate" : "Bearer"})
    
    token = create_access_token({"sub" : existing_user.username})
    return Token(access_token=token, token_type="bearer")


@router.post("/register")
async def register(user: Annotated[RegisterRequest, Body()], session : SessionDep):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = password_hash.hash(user.password)
    new_user = User(username=user.username, password=hashed_password, provider="local", provider_user_id=user.username)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message" : "User registered successfully, please login"}




@router.get("/me", response_model=UserBase)
async def read_current_user(current_user: UserDep) -> UserBase:
    return current_user


# TODOs
# 1. Abstract the type of response with a message and data, so that we can have a consistent response format across the app
# 2. Modularize 400 and 401 error for invalid creds 