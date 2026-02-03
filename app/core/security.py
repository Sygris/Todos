import os
import secrets
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.models.user import ROLE, User as UserDB

load_dotenv()

# ===== Password Hashing =====
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========== JWT ===========
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY not set")

if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES not set")


def create_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = data.copy()
    payload["exp"] = expire

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def read_token(token: str = Depends(oauth2)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def get_current_user(
    token: dict = Depends(read_token), db: Session = Depends(get_db)
) -> UserDB:
    user_id = token.get("sub")

    if user_id is None:
        raise HTTPException(status_code=401, detail="User not found")

    user = db.get(UserDB, user_id)

    if not user:
        raise HTTPException(status_code=401)

    return user


def require_role(required_role: ROLE):
    def dependency(current_user: UserDB = Depends(get_current_user)) -> UserDB:
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient Permission")

        return current_user

    return dependency
