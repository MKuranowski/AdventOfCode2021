from enum import Enum, auto

Point = tuple[int, int]
Points = list[Point]

# Test input
# TARGET_LEFT = 20
# TARGET_RIGHT = 30
# TARGET_UP = -5
# TARGET_DOWN = -10

# Real input
TARGET_LEFT = 269
TARGET_RIGHT = 292
TARGET_UP = -44
TARGET_DOWN = -68


class ShotResult(Enum):
    WITHIN = auto()
    UNDERSHOT = auto()
    OVERSHOT = auto()


def within(x: int, y: int) -> bool:
    return TARGET_LEFT <= x <= TARGET_RIGHT and TARGET_DOWN <= y <= TARGET_UP


def shoot(vel_x: int, vel_y: int) -> tuple[ShotResult, Points]:
    steps: Points = [(0, 0)]
    x = 0
    y = 0

    while True:
        x += vel_x
        y += vel_y

        steps.append((x, y))

        if within(x, y):
            return ShotResult.WITHIN, steps

        vel_x -= 1 if vel_x else 0
        vel_y -= 1

        # Basic bound checks
        if x > TARGET_RIGHT:
            return ShotResult.OVERSHOT, steps

        if y < TARGET_DOWN:
            return ShotResult.UNDERSHOT, steps

        # Other situations where we can break
        if vel_x == 0 and x < TARGET_LEFT:
            return ShotResult.UNDERSHOT, steps


def brute_force_max_y() -> int:
    max_y = -1

    for vel_x in range(1, TARGET_LEFT//2):
        for vel_y in range(500):
            result, steps = shoot(vel_x, vel_y)
            this_max_y = max(y for (_, y) in steps)

            if result == ShotResult.WITHIN and this_max_y >= max_y:
                max_y = this_max_y

            elif result == ShotResult.OVERSHOT:
                break

    return max_y


if __name__ == "__main__":
    result = brute_force_max_y()
    print(result)
