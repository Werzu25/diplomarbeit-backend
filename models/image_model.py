import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from database.init import Base
from dataclasses import dataclass

@dataclass
class ImageModel(Base):
    __tablename__ = 'images'

    id: int
    path: str
    width: int
    height: int
    creation_date: datetime.datetime

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=False)
    prediction:Mapped["PredictionModel"] = relationship("PredictionModel", back_populates="image")
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    creation_date: Mapped[DateTime] = mapped_column(DateTime)