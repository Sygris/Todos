from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_refresh_token,
    create_token,
    get_current_user,
    hash_password,
    read_token,
    verify_password,
)
from app.models.user import User as UserDB
from app.schemas.user import RefreshRequest, Token, UserCreate, UserLogin, UserPublic

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

    access_token = create_token(
        {"sub": str(existing_user.id), "role": existing_user.role.value}
    )

    refresh_token = create_refresh_token()

    existing_user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)
):
    current_user.refresh_token = None
    db.commit()

    return {"logout": "ok"}


@router.post("/refresh")
def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    stmt = select(UserDB).where(UserDB.refresh_token == data.refresh_token)
    user = db.execute(stmt).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    new_access_token = create_token({"sub": str(user.id), "role": user.role.value})

    return {"access_token": new_access_token, "token_type": "bearer"}
