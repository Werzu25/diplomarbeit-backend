import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String
from database.init import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name:Mapped[str] = mapped_column(nullable=False, unique=True)
    email:Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name:Mapped[str] = mapped_column(nullable=True)
    last_name:Mapped[str] = mapped_column(nullable=True)
    password:Mapped[str] = mapped_column(nullable=True)
    creation_date:Mapped[DateTime] = mapped_column(DateTime,nullable=True)