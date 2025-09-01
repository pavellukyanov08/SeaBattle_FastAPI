def process_shot(board, ships, x, y):
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
    cell = board[y][x]

    if cell == 0:
        board[y][x] = -1
        return 'miss'

    if cell in (-1, -2):
        return 'already'

    ship_id = cell
    board[y][x] = -2

    ship = next((s for s in ships if s['id'] == ship_id), None)
    if ship is None:
        return 'hit'

    killed = all(board[cy][cx] == -2 for (cx, cy) in ship['coords'])
    return 'killed' if killed else 'hit'


def all_ships_destroyed(board) -> bool:
    """
    Возвращает True, если все корабли уничтожены (на доске нет cell > 0).
    """
    return all(cell <= 0 for row in board for cell in row)