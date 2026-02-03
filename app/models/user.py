from enum import Enum
from sqlalchemy import Boolean, DateTime, String, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ROLE(Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[ROLE] = mapped_column(SQLEnum(ROLE), default=ROLE.USER)
    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
