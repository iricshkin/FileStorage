from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore

from core.config import app_settings
from schemas.user import TokenData, User
from services import my_logger

logger = my_logger.get_logger(__name__)


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')


def verify_password(plain_password: Any, hashed_password: Any) -> Any:
    """Проверка соответствия полученного пароля сохраненному хэшу."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(db: AsyncSession, username: str) -> Any:
    statement = select(User).where(User.username == username)
    results = await db.execute(statement=statement)
    return results.scalar_one_or_none()


def authenticate_user(db: AsyncSession, username: str, password: str) -> bool | Any:
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):  # type: ignore
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> Any:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, app_settings.secret_key, algorithm=app_settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(auth: str = Depends(oauth2_scheme)) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(
            auth, app_settings.secret_key, algorithms=[app_settings.ALGORITHM]
        )
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.exception('Exception at get_current func for token %s', auth)
        raise credentials_exception
    user = get_user(User, username=token_data.username)  # type: ignore
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> str:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


async def get_token(db: AsyncSession, username: str, password: str) -> dict:
    user: Union[User, bool] = await authenticate_user(db, username, password)  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(
        minutes=app_settings.access_token_expire_minutes
    )
    token = create_access_token(
        data={'sub': user.username},  # type: ignore
        expires_delta=access_token_expires,
    )
    return {'access_token': token, 'token_type': 'bearer'}
