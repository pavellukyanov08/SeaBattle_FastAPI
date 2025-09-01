from random import randint, choice

def generate_board(size: int = 10):
    """
    Генерация доски с расстановкой кораблей:
    - 1 корабль на 4 клетки
    - 2 корабля на 3 клетки
    - 3 корабля на 2 клетки
    - 4 корабля на 1 клетку
    """
    board = [[0 for _ in range(size)] for _ in range(size)]
    ships_config, ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1], []

    def can_place(x: int, y: int, length: int, horizontal: bool):
        # проверка выхода за границы
        if horizontal and x + length > size:
            return False
        if not horizontal and y + length > size:
            return False

        for i in range(length):
            cx = x + i if horizontal else x
            cy = y if horizontal else y + i

            if board[cy][cx] != 0:
                return False

            # проверяем соседние клетки (включая диагонали)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    ny, nx = cy + dx, cx + dy
                    if 0 <= ny < size and 0 <= nx < size:
                        if board[ny][nx] != 0:
                            return False
        return True

    def place_ship(length: int, ship_id: int):
        for _ in range(1000):  # ограничение попыток
            x, y = randint(0, size - 1), randint(0, size - 1)
            horizontal = choice([True, False])
            if can_place(x, y, length, horizontal):
                coords = []
                for i in range(length):
                    cx = x + i if horizontal else x
                    cy = y if horizontal else y + i
                    board[cy][cx] = ship_id
                    coords.append((cx, cy))
                return coords
        raise RuntimeError(f"Не удалось разместить корабль длиной {length}")

    ship_id = 1
    for length in ships_config:
        coords = place_ship(length, ship_id)
        ships.append({"id": ship_id, "coords": coords})
        ship_id += 1

    filled = sum(cell > 0 for row in board for cell in row)
    if filled != 20:
        raise ValueError(f"Ошибка генерации: занято {filled} клеток, ожидалось 20")

    return {"board": board, "ships": ships}
