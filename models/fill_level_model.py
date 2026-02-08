import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Numeric, CheckConstraint, ForeignKey
from db.init import Base


class FillLevelModel(Base):
    __tablename__ = "fill_levels"

    id: Mapped[int] = mapped_column(primary_key=True)

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    device: Mapped["DeviceModel"] = relationship(back_populates="fill_level")

    last_update: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.now(), nullable=False)

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
    fill_level_waste: Mapped[float] = mapped_column(
        Numeric(3, 2),
        CheckConstraint("fill_level_waste >= 0 AND fill_level_waste <= 1"),
        nullable=False
    )