from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from database.init import Base

class DeviceModel(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_name: Mapped[str] = mapped_column(nullable=False)
    location: Mapped[str] = mapped_column(nullable=True)
    device_up: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_update: Mapped[DateTime] = mapped_column(DateTime)

    predictions: Mapped[list["PredictionModel"]] = relationship(
        "PredictionModel", back_populates="device"
    )

    # siehe Punkt 2 (FillLevel) – das ist bei dir auch inkonsistent
    fill_level: Mapped["FillLevelModel"] = relationship(
        "FillLevelModel", back_populates="device", uselist=False
    )
    
    def __repr__(self) -> str:
        return f"Device(id={self.id}, device_name='{self.device_name}', location='{self.location}', device_up={self.device_up}, last_update={self.last_update})"