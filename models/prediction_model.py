import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum
from database.init import Base
from dataclasses import dataclass

class LabelTypes(enum.Enum):
    GLASS = 1
    PAPER = 2
    PLASTIC = 3
    METAL = 4

@dataclass
class PredictionModel(Base):
    __tablename__ = 'predictions'

    id: int
    image_id: int
    device_id: int
    prediction_label: LabelTypes
    confidence: float
    real_label: LabelTypes | None
    id: Mapped[int] = mapped_column(primary_key=True)
    
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"))
    image: Mapped["ImageModel"] = relationship("ImageModel", back_populates="prediction")
    
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    device: Mapped["DeviceModel"] = relationship("DeviceModel", back_populates="predictions")

    prediction_label: Mapped[LabelTypes] = mapped_column()
    confidence: Mapped[float] = mapped_column()
    real_label: Mapped[LabelTypes] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"Prediction(id={self.id}, image_id={self.image_id}, device_id='{self.device_id}', prediction_label={self.prediction_label}, confidence={self.confidence}, real_label={self.real_label})"