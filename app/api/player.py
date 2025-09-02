from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.models import Player
from app.schemas.player import PlayerRead
from app.core.database import get_session


router = APIRouter()


@router.get("/players", response_model=List[PlayerRead])
async def get_players(player: Optional[str] = None, db: AsyncSession = Depends(get_session)):
    stmt = select(Player).where(Player.is_playing == False)

    if player is not None:
        stmt = stmt.where(Player.id == player)
        if not stmt:
            raise HTTPException(status_code=404, detail="Игрок не найден")

    result = await db.execute(stmt)
    players = result.scalars().all()

    if not players:
        raise HTTPException(status_code=404, detail='Ни одного игрока не зарегистрировано')

    return [PlayerRead.model_validate(player) for player in players]

