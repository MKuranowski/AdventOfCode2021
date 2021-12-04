from fileinput import FileInput

import core
from day04a import Board


def main(lines: list[str]) -> int:
    grouped_lines = core.split_on(lines, core.empty_str)
    numbers: list[int] = [int(i) for i in grouped_lines[0][0].split(",")]
    boards: list[Board] = [Board.from_lines(i) for i in grouped_lines[1:]]

    for number in numbers:
        for board in boards:
            board.mark(number)

        # If only one left - and it's won - calculate its score
        if len(boards) < 2 and boards[0].has_won():
            return boards[0].score() * number

        # Remove winning boards
        boards = [i for i in boards if not i.has_won()]

    assert False, "no winning board"


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    result = main([i.rstrip() for i in input])
    print(result)
