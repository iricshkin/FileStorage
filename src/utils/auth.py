from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str):  # type: ignore
    """Хеширование пароля."""
    return pwd_context.hash(password)
