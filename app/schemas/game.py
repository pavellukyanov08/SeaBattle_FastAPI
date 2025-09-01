from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime
from uuid import UUID


class GameCreate(BaseModel):
    player1_id: str
    player2_id: str


class GameRead(BaseModel):
    id: str
    status: str
    created_at: datetime.datetime
    winner_id: Optional[str]

    model_config = {
        "from_attributes": True
    }


class GameResponse(BaseModel):
    id: UUID
    status: str
    player1_id: UUID
    player2_id: UUID
    board1: Dict[str, Any]
    board2: Dict[str, Any]
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }


class Move(BaseModel):
    x: int
    y: int


class BoardRead(BaseModel):
    player_id: str
    state: dict
    moves: List[dict]
