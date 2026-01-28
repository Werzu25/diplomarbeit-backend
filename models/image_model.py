import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from db.init import Base

class ImageModel(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=False)
    prediction: Mapped["PredictionModel"] = relationship(
        "PredictionModel",
        back_populates="image",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    creation_date: Mapped[DateTime] = mapped_column(DateTime)
