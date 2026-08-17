"""Роуты игры: /api/game/* (см. contracts/api.md)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.api.auth import AuthenticatedPlayer, get_authenticated_player
from src.db.session import get_session
from src.models.game_session import SessionOutcome
from src.services.eligibility_service import NotEligibleError, get_eligibility
from src.services.game_session_service import GameSessionService

router = APIRouter(prefix="/api/game", tags=["game"])

DbSession = Annotated[Session, Depends(get_session)]
CurrentPlayer = Annotated[AuthenticatedPlayer, Depends(get_authenticated_player)]


def _session_summary(session) -> dict:
    return {"session_id": session.id, "outcome": session.outcome.value}


@router.get("/status")
def get_status(player: CurrentPlayer, db: DbSession) -> dict:
    eligibility = get_eligibility(db, player.telegram_id)
    return {
        "eligible": eligibility.eligible,
        "next_eligible_at": eligibility.next_eligible_at,
        "active_session": (
            _session_summary(eligibility.active_session) if eligibility.active_session else None
        ),
    }


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(player: CurrentPlayer, db: DbSession) -> dict:
    service = GameSessionService(db)
    try:
        session = service.create_session(player.telegram_id)
    except NotEligibleError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder({"next_eligible_at": exc.next_eligible_at}),
        )
    return {"session_id": session.id, "started_at": session.started_at}


@router.post("/sessions/{session_id}/reveal")
def reveal_session(session_id: str, player: CurrentPlayer, db: DbSession) -> dict:
    service = GameSessionService(db)
    session = service.reveal_session(player.telegram_id, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")

    if session.outcome == SessionOutcome.WIN:
        prize = session.prize
        return {
            "outcome": "win",
            "prize": {
                "code": prize.code,
                "discount_value": prize.discount_value,
                "expires_at": prize.expires_at,
            },
        }

    return {
        "outcome": "no_win",
        "next_eligible_at": session.player.next_eligible_at,
    }
