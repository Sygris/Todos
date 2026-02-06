from typing import Sequence
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session
from app.models.todo import Todo


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, todo: Todo) -> Todo:
        try:
            self.db.add(todo)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(todo)
        return todo

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.db.get(Todo, todo_id)

    def list_todos(
        self,
        completed: bool | None,
        sort_by: str,
        order: str,
        skip: int,
        limit: int,
    ) -> Sequence[Todo]:
        stmt = select(Todo)

        if completed is not None:
            stmt = stmt.where(Todo.completed == completed)

        if order == "asc":
            stmt = stmt.order_by(asc(sort_by))
        else:
            stmt = stmt.order_by(desc(sort_by))

        stmt = stmt.offset(skip).limit(limit)

        return self.db.execute(stmt).scalars().all()

    def list_by_owner(
        self,
        owner_id: int,
        completed: bool | None,
        sort_by: str,
        order: str,
        skip: int = 0,
        limit: int = 10,
    ) -> Sequence[Todo]:
        # Select user's todos
        stmt = select(Todo).where(Todo.owner_id == owner_id)

        # Filter todos by completion
        if completed is not None:
            stmt = stmt.where(Todo.completed == completed)

        if order == "asc":
            stmt = stmt.order_by(asc(sort_by))
        else:
            stmt = stmt.order_by(desc(sort_by))

        # Todos pagination
        stmt = stmt.offset(skip).limit(limit)

        return self.db.execute(stmt).scalars().all()

    def update(self, todo: Todo) -> Todo:
        try:
            self.db.commit()
            self.db.refresh(todo)
        except Exception:
            self.db.rollback()
            raise

        return todo

    def delete(self, todo: Todo) -> None:
        try:
            self.db.delete(todo)
            self.db.commit()
        except Exception:
            self.db.rollback()
