from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from app.core.security import get_current_user, require_role
from app.schemas.user import UserPublic
from app.models.user import User as UserDB, ROLE
from app.utils.init_db import create_tables
from app.routers.auth import router as authRouter
from app.routers.todos import router as todoRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialising API...")
    create_tables()
    print("Database has been initialised")
    yield
    print("Closing API")


app = FastAPI(lifespan=lifespan)
app.include_router(authRouter)
app.include_router(todoRouter)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/profile", response_model=UserPublic)
def profile(current_user: UserDB = Depends(get_current_user)):
    return current_user


@app.get("/admin", response_model=UserPublic)
def admin_dashboard(admin: UserDB = Depends(require_role(ROLE.ADMIN))):
    return admin
