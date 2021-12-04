from dataclasses import dataclass
from fileinput import FileInput
from itertools import chain
from typing import Sequence

import core

BOARD_SIZE = 5


@dataclass
class Field:
    number: int
    is_marked: bool = False


@dataclass
class Board:
    fields: list[list[Field]]

    def column(self, idx: int) -> list[Field]:
        return [row[idx] for row in self.fields]

    def row(self, idx: int) -> list[Field]:
        return self.fields[idx]

    def has_won(self) -> bool:
        for idx in range(BOARD_SIZE):
            if all(f.is_marked for f in self.row(idx)) \
                    or all(f.is_marked for f in self.column(idx)):
                return True

        return False

    def score(self) -> int:
        return sum(f.number for row in self.fields for f in row if not f.is_marked)

    def mark(self, number: int) -> None:
        for field in chain.from_iterable(self.fields):
            if field.number == number:
                field.is_marked = True

    @classmethod
    def from_lines(cls, lines: Sequence[str]) -> "Board":
        fields = [[Field(int(entry)) for entry in line.split()] for line in lines]
        assert len(fields) == BOARD_SIZE
        for row in fields:
            assert len(row) == BOARD_SIZE
        return cls(fields)


def main(lines: list[str]) -> int:
    grouped_lines = core.split_on(lines, core.empty_str)
    numbers: list[int] = [int(i) for i in grouped_lines[0][0].split(",")]
    boards: list[Board] = [Board.from_lines(i) for i in grouped_lines[1:]]

    for number in numbers:
        for board in boards:
            board.mark(number)
            if board.has_won():
                return number * board.score()

    assert False, "no winning board"


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    result = main([i.rstrip() for i in input])
    print(result)
