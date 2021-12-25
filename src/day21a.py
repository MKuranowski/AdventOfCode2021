import re
from fileinput import FileInput
from itertools import cycle
from typing import Iterable, Optional, Protocol


class DeterministicDice:
    def __init__(self, limit: int) -> None:
        self.state: int = -1
        self.limit: int = limit
        self.roll_count: int = 0

    def roll(self) -> int:
        self.roll_count += 1
        self.state = (self.state + 1) % self.limit
        return self.state + 1  # offset for the modulus


class DiceLike(Protocol):
    def roll(self) -> int: ...


class Player:
    def __init__(self, start_pos: int, board_size: int, dice: DiceLike) -> None:
        self.pos: int = start_pos
        self.board_size: int = board_size
        self.score: int = 0
        self.dice: DiceLike = dice

    def move(self) -> None:
        advance = self.dice.roll() + self.dice.roll() + self.dice.roll()
        self.pos = (self.pos + advance) % self.board_size
        self.score += self.pos + 1  # 1 to offset from the modulus


def parse_player_positions(input: Iterable[str]) -> tuple[int, int]:
    p1_pos = -1
    p2_pos = -1

    for line in input:
        m = re.match(r"Player (\d)+ starting position: (\d)+", line)
        assert m
        if m[1] == "1":
            p1_pos = int(m[2])
        elif m[1] == "2":
            p2_pos = int(m[2])
        else:
            raise RuntimeError(f"invalid player: {m[1]}")

    assert p1_pos >= 0
    assert p2_pos >= 0
    return p1_pos, p2_pos


if __name__ == "__main__":
    p1_start_pos, p2_start_pos = parse_player_positions(FileInput())

    p: Optional[Player] = None

    dice = DeterministicDice(100)
    p1 = Player(p1_start_pos - 1, 10, dice)
    p2 = Player(p2_start_pos - 1, 10, dice)

    for p in cycle((p1, p2)):
        p.move()
        if p.score >= 1000:
            break

    assert p is not None
    lost = p1 if p is p2 else p2
    print(lost.score * dice.roll_count)
