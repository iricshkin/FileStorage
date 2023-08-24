from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class BaseORM(BaseModel):
    class Config:
        orm_mode = True


class FileStorageBase(BaseORM):
    id: UUID
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool


class FileStorageInDB(FileStorageBase):
    @field_validator('created_at')
    def datetime_to_str(self, value):  # type: ignore
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value


class FileStorage(FileStorageBase):
    @field_validator('created_at', pre=True)
    def datetime_to_str(self, value):  # type: ignore
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value


class FilesList(BaseORM):
    account_id: UUID
    files: list


class Path(BaseORM):
    path: str
