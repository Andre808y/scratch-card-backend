"""Игровая логика попытки: старт раунда и раскрытие результата (FR-003, FR-004, FR-006, FR-008)."""

import random
import threading
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import settings
from src.logging_config import log_event
from src.models.game_session import GameSession, SessionOutcome
from src.models.player import Player
from src.models.prize import PrizeStatus
from src.models.prize_pool import PrizePool
from src.services.eligibility_service import NotEligibleError, get_active_pending_session
from src.services.prize_selection import select_prize
from src.services.promo_code import generate_code
from src.time_utils import utcnow

# Срок действия промокода не зафиксирован в спецификации отдельно — используется разумное
# значение по умолчанию (30 дней), см. Assumptions в spec.md.
PRIZE_VALIDITY_DAYS = 30

# SQLite на этом масштабе (см. Scale/Scope в plan.md) обслуживается одним процессом — блокировка
# на уровне процесса достаточна, чтобы проверка права на попытку и создание попытки были
# атомарны относительно параллельных запросов (research.md, п. 6), без внешнего лока/очереди.
_create_session_lock = threading.Lock()


class GameSessionService:
    def __init__(self, db: Session, rng: random.Random | None = None) -> None:
        self.db = db
        self.rng = rng or random.Random()

    def _get_or_create_player(self, telegram_id: int) -> Player:
        player = self.db.get(Player, telegram_id)
        if player is None:
            player = Player(telegram_id=telegram_id, created_at=utcnow())
            self.db.add(player)
            self.db.flush()
        return player

    def _get_active_pool(self, at: datetime) -> PrizePool | None:
        pools = self.db.execute(select(PrizePool)).scalars().all()
        for pool in pools:
            if pool.is_active(at):
                return pool
        return None

    def create_session(self, telegram_id: int) -> GameSession:
        """Создаёт попытку и сразу определяет результат на сервере (FR-004), не раскрывая его.

        Транзакционно проверяет право на попытку перед созданием, чтобы исключить состояние
        гонки между параллельными запросами с разных устройств одного аккаунта (FR-007,
        см. research.md, п. 6). Повторный вызов при уже существующей незавершённой попытке
        возвращает её же, не создавая дубликат (edge case: разрыв соединения на раунде).
        """
        with _create_session_lock:
            now = utcnow()
            player = self._get_or_create_player(telegram_id)

            active_session = get_active_pending_session(self.db, telegram_id)
            if active_session is not None:
                return active_session

            if player.next_eligible_at is not None and player.next_eligible_at > now:
                raise NotEligibleError(next_eligible_at=player.next_eligible_at)

            session = GameSession(
                player_id=player.telegram_id,
                started_at=now,
                outcome=SessionOutcome.PENDING,
            )
            self.db.add(session)
            player.next_eligible_at = now + timedelta(hours=settings.play_cooldown_hours)
            self.db.flush()

            pool = self._get_active_pool(now)
            if pool is not None:
                prize = select_prize(pool, self.rng)
                if prize is not None:
                    prize.status = PrizeStatus.ISSUED
                    prize.code = generate_code()
                    prize.issued_at = now
                    prize.expires_at = now + timedelta(days=PRIZE_VALIDITY_DAYS)
                    prize.issued_to_session_id = session.id
                    session.prize_id = prize.id

            # Коммит (не только flush) внутри лока — чтобы результат стал видим для следующего
            # потока до того, как он войдёт в критическую секцию (иначе внешний commit в
            # зависимости FastAPI произошёл бы уже после освобождения лока).
            self.db.commit()
            log_event("session_started", player_id=telegram_id, session_id=session.id)
            return session

    def reveal_session(self, telegram_id: int, session_id: str) -> GameSession | None:
        """Раскрывает результат попытки. Идемпотентно для уже раскрытых попыток."""
        session = self.db.get(GameSession, session_id)
        if session is None or session.player_id != telegram_id:
            return None

        if session.outcome == SessionOutcome.PENDING:
            session.completed_at = utcnow()
            session.outcome = SessionOutcome.WIN if session.prize_id else SessionOutcome.NO_WIN
            self.db.flush()
            if session.outcome == SessionOutcome.WIN:
                log_event(
                    "prize_issued",
                    player_id=telegram_id,
                    session_id=session.id,
                    prize_code=session.prize.code,
                )
            log_event(
                "session_result_determined",
                player_id=telegram_id,
                session_id=session.id,
                outcome=session.outcome.value,
            )

        return session
