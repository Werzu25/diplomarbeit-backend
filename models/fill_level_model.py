from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Numeric, CheckConstraint, ForeignKey
from database.init import Base

class FillLevelModel(Base):
    __tablename__ = "fill_levels"

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

    def __repr__(self) -> str:
        return f"FillLevel(id={self.id}, device_id='{self.device_id}', last_update={self.last_update}, fill_level_plastic={self.fill_level_plastic}, fill_level_paper={self.fill_level_paper}, fill_level_glass={self.fill_level_glass})"
