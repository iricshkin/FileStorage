from typing import Generic, Type, TypeVar
from uuid import uuid1

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore

from db.db import Base
from services import my_logger
from utils.auth import get_password_hash

logger = my_logger.get_logger(__name__)


class Repository:
    def get_by_username(self, *args, **kwargs):  # type: ignore
        raise NotImplementedError

    def create(self, *args, **kwargs):  # type: ignore
        raise NotImplementedError


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)


class UserRepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_by_username(self, db: AsyncSession, obj_in: CreateSchemaType):  # type: ignore
        obj_in_data = jsonable_encoder(obj_in)
        statement = select(self._model).where(
            self._model.username == obj_in_data['username']
        )
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    def create_obj(self, obj_in_data: dict):  # type: ignore
        extra_obj_info = {}
        user_id = str(uuid1())
        extra_obj_info['id'] = user_id
        password = obj_in_data.pop('password')
        extra_obj_info['hashed_password'] = get_password_hash(password)
        obj_in_data.update(extra_obj_info)
        return self._model(**obj_in_data)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType):  # type: ignore
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.create_obj(obj_in_data)
        try:
            db.add(db_obj)
            await db.commit()
        except SQLAlchemyError as error:
            logger.exception(
                'Exception at create for db_obj %s',
                db_obj,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error
            )
        await db.refresh(db_obj)
        return db_obj
