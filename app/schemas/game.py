from pydantic import BaseModel
from typing import Optional, List
import datetime


class GameCreate(BaseModel):
    player_ids: List[str]


class GameRead(BaseModel):
    id: str
    status: str
    created_at: datetime.datetime
    winner_id: Optional[str]

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
