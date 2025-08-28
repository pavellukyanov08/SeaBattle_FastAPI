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
    ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    def can_place(x, y, length, horizontal):
        # проверка выхода за границы
        if horizontal and x + length > size:
            return False
        if not horizontal and y + length > size:
            return False

        for i in range(length):
            mx, my = (x + i, y) if horizontal else (x, y + i)
            if board[mx][my] == 1:
                return False

            # проверяем соседние клетки (включая диагонали)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    cx, cy = mx + dx, my + dy
                    if 0 <= cx < size and 0 <= cy < size:
                        if board[cx][cy] == 1:
                            return False
        return True

    def place_ship(length):
        for _ in range(1000):  # ограничение попыток
            x, y = randint(0, size - 1), randint(0, size - 1)
            horizontal = choice([True, False])
            if can_place(x, y, length, horizontal):
                for i in range(length):
                    mx, my = (x + i, y) if horizontal else (x, y + i)
                    board[mx][my] = 1
                return
        raise RuntimeError(f"Не удалось разместить корабль длиной {length}")

    for ship in ships:
        place_ship(ship)

    return board
