from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserPublic
from app.models.user import User as UserDB
from app.utils.init_db import create_tables
from app.routers.auth import router as authRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialising API...")
    create_tables()
    print("Database has been initialised")
    yield
    print("Closing API")


app = FastAPI(lifespan=lifespan)
app.include_router(authRouter)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/profile", response_model=UserPublic)
def profile(current_user: UserDB = Depends(get_current_user)):
    return current_user
