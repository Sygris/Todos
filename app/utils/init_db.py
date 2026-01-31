from app.core.database import engine, Base
from app.models.user import User
from app.models.todo import Todo


def create_tables():
    Base.metadata.create_all(bind=engine)
