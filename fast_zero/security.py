from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode
from pwdlib import PasswordHash

SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    """Returns the enconded data using HS256 -> str"""
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encode_jwt = encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def get_password_hash(password: str):
    """Returns the password string hash -> str"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Checks if the hashed password is valid -> bool"""
    return pwd_context.verify(plain_password, hashed_password)
