import re
from enum import Enum, auto
from fileinput import FileInput
from typing import NamedTuple

Point = tuple[int, int]
Points = list[Point]

# Test input
# TARGET_LEFT = 20
# TARGET_RIGHT = 30
# TARGET_UP = -5
# TARGET_DOWN = -10

# Real input
# TARGET_LEFT = 269
# TARGET_RIGHT = 292
# TARGET_UP = -44
# TARGET_DOWN = -68


class BLTR(NamedTuple):
    bottom: int
    left: int
    top: int
    right: int

    @classmethod
    def from_input(cls, line: str) -> "BLTR":
        m = re.match(r"target area: x=(-?\d+)\.\.(-?\d+), y=(-?\d+)\.\.(-?\d+)", line)
        assert m
        return cls(
            bottom=int(m[3]),
            left=int(m[1]),
            top=int(m[4]),
            right=int(m[2]),
        )

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class ShotResult(Enum):
    WITHIN = auto()
    UNDERSHOT = auto()
    OVERSHOT = auto()


def shoot(vel_x: int, vel_y: int, target: BLTR) -> tuple[ShotResult, Points]:
    steps: Points = [(0, 0)]
    x = 0
    y = 0

    while True:
        x += vel_x
        y += vel_y

        steps.append((x, y))

        if target.contains(x, y):
            return ShotResult.WITHIN, steps

        vel_x -= 1 if vel_x else 0
        vel_y -= 1

        # Basic bound checks
        if x > target.right:
            return ShotResult.OVERSHOT, steps

        if y < target.bottom:
            return ShotResult.UNDERSHOT, steps

        # Other situations where we can break
        if vel_x == 0 and x < target.left:
            return ShotResult.UNDERSHOT, steps


def brute_force_max_y(target: BLTR) -> int:
    max_y = -1

    for vel_x in range(1, target.left//2):
        for vel_y in range(500):
            result, steps = shoot(vel_x, vel_y, target)
            this_max_y = max(y for (_, y) in steps)

            if result == ShotResult.WITHIN and this_max_y >= max_y:
                max_y = this_max_y

            elif result == ShotResult.OVERSHOT:
                break

    return max_y


if __name__ == "__main__":
    target = BLTR.from_input(next(FileInput()).strip())
    result = brute_force_max_y(target)
    print(result)
