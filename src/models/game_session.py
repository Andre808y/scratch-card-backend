"""GameSession — один раунд игры конкретного игрока (см. data-model.md)."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.player import Player
    from src.models.prize import Prize


class SessionOutcome(str, enum.Enum):
    PENDING = "pending"
    WIN = "win"
    NO_WIN = "no_win"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.telegram_id"))
    started_at: Mapped[datetime] = mapped_column(DateTime())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(), default=None)
    outcome: Mapped[SessionOutcome] = mapped_column(
        Enum(SessionOutcome), default=SessionOutcome.PENDING
    )
    prize_id: Mapped[str | None] = mapped_column(ForeignKey("prizes.id"), default=None)

    player: Mapped["Player"] = relationship(back_populates="sessions")
    prize: Mapped["Prize | None"] = relationship(foreign_keys=[prize_id])
