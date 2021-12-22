from typing import Iterable
from itertools import product

from fileinput import FileInput

Point = tuple[int, int, int]

LEFT_LIMIT = -50
RIGHT_LIMIT = 50


def parse_range(r: str) -> range:
    left, _, right = r.partition("..")
    return range(
        max(int(left), LEFT_LIMIT),
        min(int(right), RIGHT_LIMIT) + 1
    )


def points_of_line(line: str) -> Iterable[Point]:
    x_str, y_str, z_str = line.split(",")
    xs = parse_range(x_str[2:])
    ys = parse_range(y_str[2:])
    zs = parse_range(z_str[2:])
    yield from product(xs, ys, zs)


def process_line(reactor: set[Point], line: str) -> None:
    status, _, points_str = line.partition(" ")
    points = points_of_line(points_str)

    if status == "on":
        reactor.update(points)
    elif status == "off":
        reactor.difference_update(points)
    else:
        raise ValueError(f"unknown status: {status!r} ({line!r})")


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    lines = filter(None, (i.strip() for i in input))
    reactor: set[Point] = set()

    for line in lines:
        process_line(reactor, line.strip())

    print(len(reactor))
