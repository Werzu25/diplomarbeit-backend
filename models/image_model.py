from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from database.init import Base
from models.prediction_model import PredicionModel

class ImageModel(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=False)
    hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    prediction:Mapped["PredicionModel"] = relationship("PredicionModel", back_populates="image")
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    creation_date: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"Image(id={self.id}, path='{self.path}', hash='{self.hash}', width={self.width}, height={self.height}, creation_date='{self.creation_date}')"