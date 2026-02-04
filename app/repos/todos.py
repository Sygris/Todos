from typing import Sequence
from sqlalchemy import Select, select
from sqlalchemy.orm import Session
from app.models.todo import Todo


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)

        return todo

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.get(Todo, todo_id)

    def list_todos(self, completed: bool, skip: int, limit: int) -> Sequence[Todo]:
        stmt = select(Todo).where(Todo.completed == completed).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def list_by_owner(
        self, owner_id: int, completed: bool, skip: int = 0, limit: int = 10
    ) -> Sequence[Todo]:
        # Select user's todos
        stmt = select(Todo).where(Todo.owner_id == owner_id)
        # Filter todos by completion
        stmt = stmt.where(Todo.completed == completed)
        # Todos pagination
        stmt = stmt.offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def delete(self, todo: Todo) -> None:
        self.db.delete(todo)
        self.db.commit()
