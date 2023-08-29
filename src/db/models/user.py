import uuid

from sqlalchemy import Column, String  # type: ignore
from sqlalchemy.dialects.postgresql import UUID  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from db.db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        nullable=False,
    )
    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment='Имя пользователя',
    )
    password = Column(
        String(200),
        nullable=False,
        comment='Пароль пользователя',
    )
    files = relationship(
        'FileStorage', back_populates='user', passive_deletes=True
    )
