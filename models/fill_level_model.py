import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Numeric, CheckConstraint, ForeignKey
from database.init import Base
from dataclasses import dataclass

@dataclass
class FillLevelModel(Base):
    __tablename__ = "fill_levels"

    id:int
    device_id:int
    last_update:datetime.datetime
    fill_level_plastic:float
    fill_level_paper:float
    fill_level_glass:float

    id: Mapped[int] = mapped_column(primary_key=True)

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    device: Mapped["DeviceModel"] = relationship(back_populates="fill_level")

    last_update: Mapped[DateTime] = mapped_column(DateTime)

    fill_level_plastic: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("fill_level_plastic >= 0 AND fill_level_plastic <= 1"),
        nullable=False
    )
    fill_level_paper: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("fill_level_paper >= 0 AND fill_level_paper <= 1"),
        nullable=False
    )
    fill_level_glass: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("fill_level_glass >= 0 AND fill_level_glass <= 1"),
        nullable=False
    )