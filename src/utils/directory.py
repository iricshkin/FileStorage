import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from db.models.file import Directory
from services import my_logger

logger = my_logger.get_logger(__name__)


async def create_dir_info(db: AsyncSession, path: str) -> Directory:
    dir_id = str(uuid.uuid1())
    dir_info_obj = Directory(id=dir_id, path=path)
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
