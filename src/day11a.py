from fileinput import FileInput
from itertools import product
from typing import Iterable

Board = list[list[int]]
Point = tuple[int, int]

BOARD_SIZE = 10


def dump_board(b: Board):
    for row in b:
        print("".join(map(str, row)))


def neighbors(x: int, y: int) -> Iterable[Point]:
    for nx, ny in product((x-1, x, x+1), (y-1, y, y+1)):
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and not (nx == x and ny == y):
            yield nx, ny


def evolve(board: Board) -> tuple[Board, int]:
    flashed: set[Point] = set()
    to_expand: set[Point] = set()

    # Add one to every position and find initial flashes
    for x, y in product(range(BOARD_SIZE), range(BOARD_SIZE)):
        board[x][y] += 1
        if board[x][y] > 9:
            flashed.add((x, y))
            to_expand.add((x, y))

    # Bump values until no other flashes occur
    while to_expand:
        x, y = to_expand.pop()

        # Bump adjacent
        for nx, ny in neighbors(x, y):
            # Neighbor already flashed - ignore
            if (nx, ny) in flashed:
                continue

            board[nx][ny] += 1
            if board[nx][ny] > 9:
                flashed.add((nx, ny))
                to_expand.add((nx, ny))

    # Wrap around flashed to zero
    for x, y in flashed:
        board[x][y] = 0

    return board, len(flashed)


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    board = [
        [int(i) for i in line.strip()]
        for line in input
    ]
    flashes: int = 0

    for _ in range(100):
        board, current_flashes = evolve(board)
        flashes += current_flashes

    print(flashes)
