from typing import Annotated
from fastapi import Depends
from ..utils.auth_util import oauth2scheme, decode_token
from ..utils.exceptions import invalid_creds_exc
from sqlmodel import select
from .db_deps import SessionDep
from ..db.schemas.user import User, UserWithId

def get_current_user(token: Annotated[str, Depends(oauth2scheme)], session : SessionDep) :
    username = decode_token(token)
    
    current_user = session.exec(select(User).where(User.username == username)).first()
    if current_user is None or current_user.id is None:
        raise invalid_creds_exc
    return current_user
    

def is_authenticated(token: Annotated[str, Depends(oauth2scheme)]):
    decode_token(token)
    return


UserDep = Annotated[UserWithId, Depends(get_current_user)]

IsAuthenticatedDep = Depends(is_authenticated)