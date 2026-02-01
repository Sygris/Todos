from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User as UserDB
from app.schemas.user import UserCreate, UserPublic

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
