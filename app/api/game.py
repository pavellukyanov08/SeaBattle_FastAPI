import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from typing import Optional, List, Dict

from app.schemas.game import GameRead, GameCreate, GameResponse
from app.models.models import Game, Player, GameStatus
from app.core.database import get_session, AsyncSessionLocal
from app.services.board import generate_board
from app.services.shot_logic import process_shot, all_ships_destroyed
from app.ws_manager import manager
from app.core.database import get_session

router = APIRouter()

active_games: Dict[str, Dict] = {}
games: Dict[str, dict] = {}

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


@router.post("/game/create", response_model=GameResponse)
async def create_game(game: GameCreate, db: AsyncSessionLocal = Depends(get_session)):
    # player1 = select(Player).where(Player.id == game.player1_id)
    # player2 = select(Player).where(Player.id == game.player2_id)

    if game.player1_id == game.player2_id:
        raise HTTPException(status_code=400, detail="Игроки должны быть разные")

    stmt = select(Player).where(Player.id.in_([game.player1_id, game.player2_id]))
    result = await db.execute(stmt)
    players = result.scalars().all()

    if len(players) != 2:
        raise HTTPException(status_code=404, detail="Один или оба игрока не найдены")

    board1 = generate_board()
    board2 = generate_board()

    new_game = Game(
        id=str(uuid.uuid4()),
        player1_id=game.player1_id,
        player2_id=game.player2_id,
        board1=board1,
        board2=board2,
        status=GameStatus.waiting,
    )

    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)

    return new_game


async def finish_game(game_id: str, winner_id: str | None):
    async with get_session() as session:
        db_game = await session.get(Game, game_id)
        if db_game:
            db_game.winner_id = winner_id
            db_game.status = "finished"
            await session.commit()


@router.websocket("/games/{game_id}/play")
async def websocket_game(websocket: WebSocket, game_id: str):
    await manager.connect(game_id, websocket)

    if game_id not in games:
        games[game_id] = {
            'players': [],
            'turn': None,
            'boards': {},
            'ships': {},
            'winner': None,
            'started': False,
        }

    player_id = None

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get('action')
            player_id = data.get('player_id')

            if not player_id:
                await manager.send_personal(websocket, {'error': 'player_id обязателен'})
                continue

            if action == "join":
                room = games[game_id]

                if room['winner'] is not None:
                    await manager.send_personal(websocket, {'error': 'Игра уже завершена'})
                    continue

                if player_id in room['players']:
                    await manager.send_personal(websocket, {
                        'event': 'joined',
                        'player_id': player_id,
                        'players': room['players'],
                    })
                    continue

                if len(room['players']) >= 2:
                    await manager.send_personal(websocket, {'error': 'Комната заполнена'})
                    continue

                room['players'].append(player_id)

                board_data = generate_board()
                room['boards'][player_id] = board_data['board']
                room['ships'][player_id] = board_data['ships']

                # Ответ только этому игроку
                await manager.send_personal(websocket, {
                    "event": "joined",
                    "player_id": player_id,
                    "players": room['players']
                })

                # Broadcast всем о новом игроке
                await manager.broadcast(game_id, {
                    "event": "player_joined",
                    "players": room['players']
                })

            # Начало игры
            elif action == "start":
                room = games[game_id]
                if room['started']:
                    await manager.send_personal(websocket, {'error': 'Игра уже начата'})
                    continue

                if len(room['players']) != 2:
                    await manager.broadcast(websocket, {'error': 'Для старта нужны 2 игрока'})
                    continue

                room['turn'] = room['players'][0]
                room['started'] = True

                await manager.broadcast(game_id, {
                    'event': 'game_started',
                    'first_turn': room['turn']
                })

            elif action == "move":
                room = games[game_id]
                if not room['started']:
                    await manager.send_personal(websocket, {'error': 'Игра еще не начата'})
                    continue

                if player_id != room['turn']:
                    await manager.send_personal(websocket, {"error": "Не ваша попытка"})
                    continue

                x, y = data['x'], data['y']
                # валидация координат
                if not (isinstance(x, int) and isinstance(y, int) and 0 <= x < 10 and 0 <= y < 10):
                    await manager.send_personal(websocket, {"error": "Некорректные координаты"})
                    continue

                # Противник
                opponent = [p for p in games[game_id]['players'] if p != player_id][0]
                if not opponent:
                    await manager.send_personal(websocket, {"error": "Нет соперника"})
                    continue

                opponent = opponent[0]

                board = games[game_id]['boards'][opponent]
                ships = games[game_id]['ships'][opponent]

                # Логика попадания
                result = process_shot(board, ships, x, y)

                # Проверка победы
                winner = None
                if all_ships_destroyed(board):
                    winner = player_id
                    room['winner'] = winner
                    room['turn'] = None
                    room['started'] = False
                    await finish_game(game_id, winner)

                    await manager.broadcast(game_id, {
                        "event": "move_result",
                        "player": player_id,
                        "x": x, "y": y,
                        "result": result,
                        "next_turn": None,
                        "winner": winner
                    })

                    await manager.broadcast(game_id, {
                        "event": "game_over",
                        "winner": winner
                    })
                    continue

                next_turn = player_id if result in ('hit', 'kill', 'already') else opponent
                room['turn'] = next_turn

                await manager.broadcast(game_id, {
                    "event": "move_result",
                    "player": player_id,
                    "x": x, "y": y,
                    "result": result,
                    "next_turn": next_turn,
                    "winner": None
                })


            elif action == 'end':
                room = games[game_id]
                if room['winner'] is None:
                    room['winner'] = player_id
                room['turn'] = None
                room['started'] = False
                await finish_game(game_id, room['winner'])
                await manager.broadcast(game_id, {
                    "event": "game_over",
                    "winner": room['winner']
                })

            else:
                await manager.send_personal(websocket, {"error": "Неизвестное действие"})

    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)
        room = games.get(game_id)
        if room:
            await manager.broadcast(game_id, {
                "event": "player_disconnect",
                "player_id": player_id
            })

            if room.get('started') and player_id in room['players']:
                other = next((p for p in room['players'] if p != player_id), None)
                if other:
                    room['winner'] = other
                    room['started'] = False
                    room['turn'] = None
                    await finish_game(game_id, other)
                    await manager.broadcast(game_id, {
                        "event": "game_over",
                        "winner": other
                    })