from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.todo import Todo
from app.models.user import User as UserDB, ROLE
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoRead)
def create_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> TodoRead:
    todo = Todo(**data.model_dump())
    todo.owner_id = current_user.id

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@router.get("/", response_model=list[TodoRead])
def list_todos(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    if current_user.role == ROLE.ADMIN:
        stmt = select(Todo)
    else:
        stmt = select(Todo).where(Todo.owner_id == current_user.id)

    stmt = stmt.offset(skip).limit(limit)
    todos = db.execute(stmt).scalars().all()

    return todos


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> TodoRead:
    todo = db.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if current_user.role != ROLE.ADMIN and current_user.id != todo.owner_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
) -> TodoRead:
    todo = db.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if current_user.role != ROLE.ADMIN and current_user.id != todo.owner_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    for field, value in todo_data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)

    return todo


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    todo = db.get(Todo, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if current_user.role != ROLE.ADMIN and current_user.id != todo.owner_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(todo)
    db.commit()

    return {"deleted": True}
