import uuid
from datetime import datetime

from sqlalchemy import ForeignKey  # type: ignore
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import UUIDType  # type: ignore

from db.db import Base


class FileStorage(Base):
    __tablename__ = 'filestorage'
    id = Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid1,
    )
    name = Column(
        String(125),
        nullable=False,
        comment='Наименование файла',
    )
    path = Column(
        String(255),
        nullable=False,
        unique=True,
        comment='Путь файла',
    )
    size = Column(
        Integer,
        nullable=False,
        comment='Размер файла',
    )
    created_at = Column(
        DateTime,
        index=True,
        default=datetime.utcnow,
        comment='Дата создания файла',
    )
    is_downloadable = Column(
        Boolean,
        default=False,
        comment='Возможность загрузить файл',
    )
    owner = Column(
        UUIDType,
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Владелец файла',
    )
    user = relationship('User', back_populates='files')


class Directory(Base):
    __tablename__ = 'directories'
    id = Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid1,
    )
    path = Column(
        String(255),
        nullable=False,
        unique=True,
        comment='Путь директории',
    )
