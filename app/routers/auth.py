from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User as UserDB
from app.schemas.user import Token, UserCreate, UserLogin, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserPublic)
def signup(signupData: UserCreate, db: Session = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.email == signupData.email)
    existing_user = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = UserDB(**signupData.model_dump())
    user.password = hash_password(user.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(loginData: UserLogin, db: Session = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.email == loginData.email)
    existing_user = db.execute(stmt).scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Wrong credentials")

    if not verify_password(loginData.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Wrong credentials")

    access_token = create_token({"sub": str(existing_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": "AHAHAHA",
        "token_type": "bearer",
    }
