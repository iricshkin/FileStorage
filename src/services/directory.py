import uuid
from typing import Any, Generic, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore

from db.db import Base
from services import my_logger
from services.file import Repository

logger = my_logger.get_logger(__name__)


ModelType = TypeVar('ModelType', bound=Base)


class DirectoryRepositoryDB(Repository, Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_dir_info_by_path(self, db: AsyncSession, dir_path: str) -> Any:
        if not dir_path.startswith('/'):
            dir_path = '/' + dir_path
        statement = select(self._model).where(self._model.path == dir_path)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_dir_info_by_id(self, db: AsyncSession, dir_id: uuid.UUID) -> Any:
        statement = select(self._model).where(self._model.id == dir_id)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_list_by_user_object(  # type: ignore
        self,
        db: AsyncSession,
        user_obj: ModelType,
    ) -> Any:
        statement = select(self._model).where(self._model.user_id == user_obj.id)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create_dir_info(self, db: AsyncSession, path: str) -> Any:
        dir_info_obj = self._model(path=path)
        try:
            db.add(dir_info_obj)
            await db.commit()
        except SQLAlchemyError as error:
            logger.exception(
                'Exception at create_dir_info for dir_info_obj %s',
                dir_info_obj,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error
            )
        await db.refresh(dir_info_obj)
        return dir_info_obj
