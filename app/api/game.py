from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from typing import Optional, List, Dict

from app.schemas.game import GameRead
from app.models.models import Game
from app.core.database import get_session, AsyncSessionLocal

router = APIRouter()

active_games: Dict[str, Dict] = {}


@router.get("/games", response_model=List[GameRead])
async def get_games(game: Optional[str] = None, db: AsyncSessionLocal = Depends(get_session)):
    stmt = select(Game).where(Game.status == 'playing')

    if game is not None:
        stmt = stmt.where(Game.id == game)
        if not stmt:
            raise HTTPException(status_code=404, detail="Игра не найдена")

    result = await db.execute(stmt)
    games = result.scalars().all()

    if not games:
        raise HTTPException(status_code=404, detail='Ни одной игры не создано')

    return [GameRead.model_validate(game) for game in games]


@router.websocket("/games/game_id/play}")
async def create_game(websocket: WebSocket, game_id: str, db: AsyncSessionLocal = Depends(get_session)):
    await websocket.accept()

    if game_id not in active_games:
        active_games[game_id] = {"players": {}}
    active_games[game_id]["players"].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get("action")
            player_id = data.get("player_id")

            if action == "start":
                for ws in active_games[game_id]["players"]:
                    await ws.send_json({"event": "game_started"})

            elif action == "move":
                x, y = data.get["x"], data.get["y"]

                game = db.query(Game).filter(Game.id == game_id).first()
                board = game.board2 if player_id==player_id.id else game.board1

                result = "miss"
                if board[x][y] == 1:
                    board[x][y] = -1  # отмечаем попадание
                    result = "hit"
                    if not any(1 in row for row in board):  # проверка победы
                        result = "win"
                        game.status = "finished"
                        game.winner_id = player_id
                        db.commit()

                # отсылаем всем результат хода
                for ws in active_games[game_id]["players"]:
                    await ws.send_json({"event": "move", "player": player_id, "x": x, "y": y, "result": result})

            elif action == "end":
                for ws in active_games[game_id]["players"]:
                    await ws.send_json({"event": "game_ended"})
                game = db.query(Game).filter(Game.id == game_id).first()
                game.status = "finished"
                db.commit()

    except WebSocketDisconnect:
        active_games[game_id]["players"].remove(websocket)
        if not active_games[game_id]["players"]:
            del active_games[game_id]



