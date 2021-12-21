from itertools import cycle
from typing import Optional, Protocol

P1_START_POS = 7  # 7 for real input, 4 for test input
P2_START_POS = 4  # 4 for real input, 8 for test input


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


if __name__ == "__main__":
    p: Optional[Player] = None

    dice = DeterministicDice(100)
    p1 = Player(P1_START_POS - 1, 10, dice)
    p2 = Player(P2_START_POS - 1, 10, dice)

    for p in cycle((p1, p2)):
        p.move()
        if p.score >= 1000:
            break

    assert p is not None
    lost = p1 if p is p2 else p2
    print(lost.score * dice.roll_count)
