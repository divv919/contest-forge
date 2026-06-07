from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from ..db.schemas.user import User, UserWithId
from ..utils.auth_util import decode_token, oauth2scheme
from ..utils.exceptions import invalid_creds_exc
from .db_deps import SessionDep


def get_current_user(token: Annotated[str, Depends(oauth2scheme)], session: SessionDep):
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
