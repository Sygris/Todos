from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.todo import Todo
from app.models.user import User as UserDB
from app.services.todos import TodoService
from app.repos.todos import TodoRepository
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead, status_code=201)
def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = TodoService(TodoRepository(db))
    return service.create_todo(data, current_user)


@router.get("/", response_model=list[TodoRead], status_code=200)
def list_todos(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    completed: bool | None = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    service = TodoService(TodoRepository(db))

    return service.list_todos(current_user, completed, sort_by, order, skip, limit)


@router.get("/{todo_id}", response_model=TodoRead, status_code=200)
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


@router.patch("/{todo_id}", response_model=TodoRead, status_code=200)
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


@router.delete("/{todo_id}", status_code=204)
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
