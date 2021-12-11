from fileinput import FileInput

from core import iterate
from day11a import BOARD_SIZE, evolve

if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    board = [
        [int(i) for i in line.strip()]
        for line in input
    ]
    target_flashes = BOARD_SIZE ** 2

    for step in iterate(lambda i: i + 1, 1):
        board, current_flashes = evolve(board)
        if current_flashes == target_flashes:
            print(step)
            break
