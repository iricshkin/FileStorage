from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from schemas.file import FileStorage


class BaseORM(BaseModel):
    class Config:
        orm_mode = True


class Token(BaseORM):
    access_token: str
    token_type: str


class TokenData(BaseORM):
    username: str | None = None


class User(BaseORM):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserRegisterAuth(User):
    password: str


class CurrentUser(User):
    id: UUID
    created_at: datetime

    @field_validator('created_at', pre=True)
    def datetime_to_str(self, value):  # type: ignore
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            return value


class UserInDB(CurrentUser):
    hashed_password: str
    files: list[FileStorage] = []
