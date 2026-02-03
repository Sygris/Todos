from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.todo import Todo
from app.models.user import User as UserDB
from app.schemas.todo import TodoCreate, TodoRead

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead)
def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> Todo:
    todo = Todo(**data.model_dump())
    todo.owner_id = current_user.id

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@router.get("/", response_model=list[TodoRead])
def list_todos(
    db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)
):
    stmt = select(Todo).where(Todo.owner_id == current_user.id)

    todos = db.execute(stmt).scalars().all()
    return todos
