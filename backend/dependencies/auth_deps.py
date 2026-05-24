from typing import Annotated
from ..utils.auth_util import oauth2scheme, decode_token
from ..utils.exeptions import invalid_creds_exc
from sqlmodel import select
from .db_deps import SessionDep
from ..db.schemas.user import User, UserBase

def get_current_user(token: Annotated[str, oauth2scheme], session : SessionDep) -> UserBase:
    username = decode_token(token)
    
    current_user = session.exec(select(User).where(User.username == username)).first()
    if current_user is None:
        raise invalid_creds_exc
    return current_user
    