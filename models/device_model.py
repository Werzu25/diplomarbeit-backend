import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from db.init import Base


class DeviceModel(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_name: Mapped[str] = mapped_column(nullable=False, unique=True)
    location: Mapped[str] = mapped_column(nullable=True)
    device_up: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_update: Mapped[DateTime] = mapped_column(DateTime,nullable=True)

    predictions: Mapped[list["PredictionModel"]] = relationship(
        "PredictionModel", back_populates="device"
    )

    fill_level: Mapped["FillLevelModel"] = relationship(
        "FillLevelModel", back_populates="device", uselist=False
    )