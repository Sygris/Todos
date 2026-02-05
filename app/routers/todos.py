from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, true
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.todo import Todo
from app.models.user import User as UserDB, ROLE
from app.repos.todos import TodoRepository
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from app.repos.todos import TodoRepository
from app.services.todos import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead)
def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = TodoService(TodoRepository(db))
    return service.create_todo(data, current_user)


@router.get("/", response_model=list[TodoRead])
def list_todos(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 10,
):
    service = TodoService(TodoRepository(db))

    return service.list_todos(current_user, completed, skip, limit)


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> Todo:
    service = TodoService(TodoRepository(db))

    try:
        return service.get_todo(todo_id, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found!")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> Todo:
    service = TodoService(TodoRepository(db))

    try:
        return service.update_todo(
            todo_id, current_user, todo_data.model_dump(exclude_unset=True)
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = TodoService(TodoRepository(db))

    try:
        service.delete_todo(todo_id, current_user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Todo not found")
    except PermissionError:
        raise HTTPException(status_code=401, detail="Forbidden")

    return {"deleted": True}
