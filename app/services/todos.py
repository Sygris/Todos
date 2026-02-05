from typing import Sequence
from app.models.todo import Todo
from app.models.user import User, ROLE
from app.repos.todos import TodoRepository


class TodoService:
    def __init__(self, repo: TodoRepository):
        self.repo = repo

    def create_todo(self, data, user: User) -> Todo:
        todo = Todo(**data.model_dump())
        todo.owner_id = user.id
        return self.repo.create(todo)

    def list_todos(
        self, user: User, completed: bool | None, skip: int, limit: int
    ) -> Sequence[Todo]:
        if user.role == ROLE.ADMIN:
            return self.repo.list_todos(completed, skip, limit)
        return self.repo.list_by_owner(user.id, completed, skip, limit)

    def get_todo(self, todo_id: int, user: User) -> Todo:
        todo = self.repo.get_by_id(todo_id)

        if not todo:
            raise ValueError("Todo not Found")

        if user.role != ROLE.ADMIN and todo.owner_id != user.id:
            raise PermissionError("Forbidden")

        return todo

    def update_todo(self, todo_id: int, current_user: User, data: dict):
        todo = self.get_todo(todo_id, current_user)

        for field, value in data.items():
            setattr(todo, field, value)

        return self.repo.update(todo)

    def delete_todo(self, todo_id: int, user: User) -> None:
        todo = self.get_todo(todo_id, user)
        self.repo.delete(todo)
