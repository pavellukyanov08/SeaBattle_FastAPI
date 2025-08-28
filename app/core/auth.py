from datetime import timedelta, datetime
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
import os

from dotenv import load_dotenv
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.models import Player

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_WEEKS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(weeks=ACCESS_TOKEN_EXPIRE_WEEKS)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(weeks=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user(db: AsyncSessionLocal, username: str) -> Optional[Player]:
    result = await db.execute(select(Player).where(Player.name == username))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSessionLocal, username: str, password: str) -> Optional[Player]:
    user = await get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user