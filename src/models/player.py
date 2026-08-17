"""Player — пользователь Telegram-бота, идентифицируемый его Telegram ID."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.game_session import GameSession


class Player(Base):
    __tablename__ = "players"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime())
    next_eligible_at: Mapped[datetime | None] = mapped_column(DateTime(), default=None)

    sessions: Mapped[list["GameSession"]] = relationship(back_populates="player")
