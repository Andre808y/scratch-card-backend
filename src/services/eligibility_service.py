"""Проверка права игрока на попытку: кулдаун и незавершённые попытки (FR-007)."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.game_session import GameSession, SessionOutcome
from src.models.player import Player
from src.time_utils import utcnow


class NotEligibleError(Exception):
    """Игрок не может начать новую попытку — попытка уже использована в текущем окне."""

    def __init__(self, next_eligible_at):
        self.next_eligible_at = next_eligible_at
        super().__init__("player is not eligible for a new attempt")


@dataclass
class EligibilityStatus:
    eligible: bool
    next_eligible_at: object
    active_session: GameSession | None


def get_active_pending_session(db: Session, telegram_id: int) -> GameSession | None:
    """Незавершённая попытка игрока, если она есть (edge case: разрыв соединения на раунде)."""
    return (
        db.execute(
            select(GameSession)
            .where(
                GameSession.player_id == telegram_id, GameSession.outcome == SessionOutcome.PENDING
            )
            .order_by(GameSession.started_at.desc())
        )
        .scalars()
        .first()
    )


def get_eligibility(db: Session, telegram_id: int) -> EligibilityStatus:
    active_session = get_active_pending_session(db, telegram_id)
    if active_session is not None:
        return EligibilityStatus(
            eligible=True, next_eligible_at=None, active_session=active_session
        )

    player = db.get(Player, telegram_id)
    now = utcnow()
    if player is not None and player.next_eligible_at is not None and player.next_eligible_at > now:
        return EligibilityStatus(
            eligible=False, next_eligible_at=player.next_eligible_at, active_session=None
        )

    return EligibilityStatus(eligible=True, next_eligible_at=None, active_session=None)
