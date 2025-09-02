from typing import List


def process_shot(board: List[List[int]], ships: List[dict], x: int, y: int) -> str:
    """
    Возвращает результат хода:
    - 'miss' – промах
    - 'hit' – попадание
    - 'kill' – уничтожен
    - 'already' – по этой клетке уже стреляли
    :param board: board[y][x]
    :param ships: список словарей {'id': int, 'coords': [(x, y), ...]}
    :param x:
    :param y:
    :return:
    """
    if board[y][x] == -1:
        return 'already'

    elif board[y][x] > 0:
        ship_id = board[y][x]
        board[y][x] = -1

        ship_destroyed = True
        for ship in ships:
            if ship['id'] == ship_id:
                for coords in ship['coords']:
                    cx, cy = coords
                    if board[cy][cx] > 0:
                        ship_destroyed = False
                        break
                break

        return 'kill' if ship_destroyed else 'hit'
    else:
        board[y][x] = -1
        return 'miss'

def all_ships_destroyed(board: List[List[int]]) -> bool:
    """
    Возвращает True, если все корабли уничтожены (на доске нет cell > 0).
    """
    for row in board:
        for cell in row:
            if cell > 0:
                return False
    return True