import os.path
from datetime import datetime
from typing import Callable, Type

from aioshutil import copyfileobj
from fastapi import File as FileObj
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from core.config import app_settings
from db.models.file import FileStorage as FileStorageModel
from db.models.user import User as UserModel
from services import my_logger

logger = my_logger.get_logger(__name__)


async def write_to_file(  # type: ignore
    file_obj: FileObj,  # type: ignore
    full_file_path: str,
):
    with open(full_file_path, 'wb') as buffer:
        await copyfileobj(file_obj.file, buffer)  # type: ignore


async def create_file(
    db: AsyncSession,
    file_path: str,
    full_file_path: str,
    create_dir_info: Callable,
    file_obj: UploadFile,
    model: Type[FileStorageModel],
    user_obj: Type[UserModel],
) -> str:
    path = app_settings.files_folder_path
    for dir_name in file_path.split('/')[1:-1]:
        path = os.path.join(path, dir_name)
        if os.path.exists(path):
            continue
        else:
            os.mkdir(path)
            await create_dir_info(db=db, path=path)
    await write_to_file(file_obj=file_obj, full_file_path=full_file_path)
    size = os.path.getsize(full_file_path)
    new_file = model(
        name=file_obj.filename,
        path=file_path,
        size=size,
        is_downloadable=True,
        user=user_obj,
    )
    try:
        db.add(new_file)
        await db.commit()
    except SQLAlchemyError as error:
        logger.exception(
            'Exception at create_file for new file %s',
            new_file,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error
        )
    await db.refresh(new_file)
    return new_file


async def put_file(
    db: AsyncSession,
    file_obj: FileObj,  # type: ignore
    full_file_path: str,
    file_info: Type[FileStorageModel],
) -> Type[FileStorageModel]:
    await write_to_file(file_obj=file_obj, full_file_path=full_file_path)
    size = os.path.getsize(full_file_path)
    file_info.size = size
    file_info.created_at = datetime.utcnow()
    await db.commit()
    await db.refresh(file_info)
    return file_info
