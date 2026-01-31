from fastapi import FastAPI
from contextlib import asynccontextmanager

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
