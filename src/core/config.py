import os
from logging import config as logging_config

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = 'filestorage.log'


class AppSettings(BaseSettings):
    app_title: str = Field('file_storage', description='Название приложения')
    project_name: str = Field(None, description='Наименование проекта')
    project_host: str = Field(description='Адрес хоста проекта')
    project_port: int = Field(description='Номер порта проекта')
    secret_key: str = Field(description='Секретный ключ приложения')
    algoritm: str = Field('HS256', description='Алгоритм шифрования пароля')
    access_token_expire_minutes: int = Field(
        30, description='Срок действия токена в минутах'
    )
    redis_host: str = Field(description='Адрес хоста redis')
    redis_port: int = Field(description='Номер порта redis')
    db_user: str = Field('postgres', description='Пользователь БД')
    db_password: str = Field('postgres', description='Пароль пользователя БД')
    db_name: str = Field('postgres', description='Наименование БД')
    db_host: str = Field('postgres', description='Адрес хоста БД')
    db_port: int = Field(description='Номер порта БД')
    database_dsn: PostgresDsn
    files_folder_path: str = Field(
        os.path.join(BASE_DIR, 'files'), env='FILES_BASE_DIR'
    )
    compression_types: list = Field(
        ['zip', '7z', 'tar'], env='COMPRESSION_TYPES'
    )
    test_dsn: str = 'postgresql+asyncpg://postgres@postgres:5342/postgres_test'

    class Config:
        env_file = '.env'


app_settings = AppSettings()
