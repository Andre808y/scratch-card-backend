"""Prize — промокод на скидку, который может получить игрок (см. data-model.md)."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.prize_pool import PrizePool


class PrizeStatus(str, enum.Enum):
    AVAILABLE_IN_POOL = "available_in_pool"
    ISSUED = "issued"
    USED = "used"
    EXPIRED = "expired"


class Prize(Base):
    __tablename__ = "prizes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prize_pool_id: Mapped[str] = mapped_column(ForeignKey("prize_pools.id"))
    code: Mapped[str | None] = mapped_column(String(64), unique=True, default=None)
    # 255, а не 32 — поле хранит не только "10%", но и свободный текст физических призов
    # ("Зарядный блок в подарок при покупке электроники" и т. п., см. data-model.md).
    discount_value: Mapped[str] = mapped_column(String(255))
    status: Mapped[PrizeStatus] = mapped_column(
        Enum(PrizeStatus), default=PrizeStatus.AVAILABLE_IN_POOL
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    issued_to_session_id: Mapped[str | None] = mapped_column(
        ForeignKey("game_sessions.id", use_alter=True, name="fk_prize_issued_session"),
        default=None,
    )
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(), default=None)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(), default=None)

    prize_pool: Mapped["PrizePool"] = relationship(back_populates="prizes")
