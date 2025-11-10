import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import settings
from .database import get_db
from . import schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_user_from_db(db: AsyncIOMotorDatabase, username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return user  
    return None

async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str) -> schemas.User | bool:
    user = await get_user_from_db(db, username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return schemas.User.model_validate(user)

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (jwt.PyJWTError, jwt.ExpiredSignatureError):
        raise credentials_exception

    user = await get_user_from_db(db, username)
    if user is None:
        raise credentials_exception
    
    return schemas.User.model_validate(user)

