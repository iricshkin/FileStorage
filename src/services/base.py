from db.models.file import Directory as DirectoryModel
from db.models.file import FileStorage as FileModel
from db.models.user import User as UserModel
from schemas.user import UserRegisterAuth
from services.directory import DirectoryRepositoryDB
from services.file import FileRepositoryDB
from services.user import UserRepositoryDB


class UserRepository(
    UserRepositoryDB[
        UserModel,
        UserRegisterAuth,
    ]
):
    pass


class FileRepository(
    FileRepositoryDB,
    FileModel,
):
    pass


class DirectoryRepository(
    DirectoryRepositoryDB[
        FileModel,
    ]
):
    pass


user_crud = UserRepository(UserModel)
file_crud = FileRepository(FileModel)
directory_crud = DirectoryRepository(DirectoryModel)
