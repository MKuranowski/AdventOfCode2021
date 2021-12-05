from collections import Counter
from fileinput import FileInput
from itertools import chain, cycle
from typing import Iterable

from day05a import Line, Point, parse_line


def points_covered_by_line(line: Line) -> set[Point]:
    xs: Iterable[int]
    ys: Iterable[int]
    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]
    sgn_dx = 1 if dx >= 0 else -1
    sgn_dy = 1 if dy >= 0 else -1

    if dx == 0:
        # Aligned with axis X.
        xs = cycle((line[0][0], ))
        ys = range(line[0][1], line[1][1] + sgn_dy, sgn_dy)

    elif dy == 0:
        # Aligned with axis Y
        xs = range(line[0][0], line[1][0] + sgn_dx, sgn_dx)
        ys = cycle((line[0][1], ))

    else:
        assert abs(dx) == abs(dy), "diagonal lines must be at 45 degrees"
        xs = range(line[0][0], line[1][0] + sgn_dx, sgn_dx)
        ys = range(line[0][1], line[1][1] + sgn_dy, sgn_dy)

    return set(zip(xs, ys))


def count_overlaps(lines: Iterable[Line]) -> int:
    counter: Counter[Point] = Counter(
        chain.from_iterable(
                points_covered_by_line(line) for line in lines
            )
    )

    return sum(1 for count in counter.values() if count > 1)


def main():
    input: "FileInput[str]" = FileInput()
    lines = (parse_line(line.strip()) for line in input)
    result = count_overlaps(lines)
    print(result)


if __name__ == "__main__":
    main()
