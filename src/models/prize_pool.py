"""PrizePool — набор доступных промокодов на период проведения акции."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.prize import Prize


class PrizePool(Base):
    __tablename__ = "prize_pools"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    active_from: Mapped[datetime] = mapped_column(DateTime())
    active_until: Mapped[datetime | None] = mapped_column(DateTime(), default=None)
    no_win_weight: Mapped[float] = mapped_column(Float)

    prizes: Mapped[list["Prize"]] = relationship(back_populates="prize_pool")

    def is_active(self, at: datetime) -> bool:
        if at < self.active_from:
            return False
        return self.active_until is None or at <= self.active_until
