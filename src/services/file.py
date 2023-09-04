from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from fastapi import File as FileObj
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore

from core.config import app_settings
from db.db import Base
from utils.directory import create_dir_info
from utils.file import create_file, put_file

ModelType = TypeVar('ModelType', bound=Base)


class Repository(ABC):
    @abstractmethod
    def get_file_info_by_path(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_file_info_by_id(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_list_by_user_object(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def create_or_put_file(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class FileRepositoryDB(Repository, Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_file_info_by_path(    # type: ignore
        self, db: AsyncSession, file_path: str
    ) -> Any:
        if not file_path.startswith('/'):
            file_path = '/' + file_path
        statement = select(self._model).where(self._model.path == file_path)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_file_info_by_id(  # type: ignore
        self, db: AsyncSession, file_id: str
    ) -> Any:
        statement = select(self._model).where(self._model.id == file_id)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_list_by_user_object(  # type: ignore
        self,
        db: AsyncSession,
        user_obj: ModelType,
    ) -> Any:
        statement = select(self._model).where(
            self._model.user_id == user_obj.id
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create_or_put_file(  # type: ignore
        self,
        db: AsyncSession,
        user_obj: ModelType,
        file_obj: FileObj,  # type: ignore
        file_path: str,
    ) -> Any:
        file_in_storage = await self.get_file_info_by_path(
            db=db, file_path=file_path
        )
        full_file_path = get_full_path(file_path)
        if file_in_storage:
            return await put_file(
                db=db,
                full_file_path=full_file_path,
                file_info=file_in_storage,
                file_obj=file_obj,
            )
        else:
            return await create_file(
                db=db,
                file_path=file_path,
                full_file_path=full_file_path,
                create_dir_info=create_dir_info,
                file_obj=file_obj,
                model=self._model,
                user_obj=user_obj,
            )


def get_full_path(path: str) -> str:
    return app_settings.files_folder_path + path
