from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from src.db.db import get_session
from src.schemas.user import Token, User, UserRegisterAuth
from src.services import my_logger
from src.services.auth import get_current_active_user, get_token
from src.services.base import user_crud

logger = my_logger.get_logger(__name__)

router = APIRouter()


@router.post(
    '/token',
    response_model=Token,
    description='Auth form for Swagger UI',
)
async def login_ui_for_access_token(
    *,
    db: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    access_token = await get_token(
        db=db, username=form_data.username, password=form_data.password
    )
    logger.info(f'Send token for {form_data.username}')
    return access_token


@router.post(
    '/auth',
    response_model=Token,
    description='Get token for user.',
)
async def get_token_for_user(
    *, db: AsyncSession = Depends(get_session), obj_in: UserRegisterAuth
) -> Any:
    username, password = obj_in.username, obj_in.password
    access_token = await get_token(db=db, username=username, password=password)
    logger.info('Send token for %s', username)
    return access_token


@router.post(
    '/register',
    response_model=UserRegisterAuth,
    status_code=status.HTTP_201_CREATED,
    description='Create new user.',
)
async def create_user(
    *, db: AsyncSession = Depends(get_session), user_in: UserRegisterAuth
) -> Any:
    """
    Create new user.
    """
    user_obj = await user_crud.get_by_username(db=db, obj_in=user_in)
    if user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this username exists.',
        )
    user = await user_crud.create(db=db, obj_in=user_in)
    logger.info('Create user - %s', user.username)
    return user


@router.get('/me/', response_model=User, description='Get current user')
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
