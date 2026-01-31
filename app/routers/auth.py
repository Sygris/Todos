from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup(signupData: UserCreate, db: Session = Depends(get_db)):
    return {"test": "ok"}
