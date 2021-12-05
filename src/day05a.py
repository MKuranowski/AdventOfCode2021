from collections import Counter
from fileinput import FileInput
from itertools import chain, cycle
from typing import Generator, Iterable

Point = tuple[int, int]
Line = tuple[Point, Point]


def parse_point(text: str) -> Point:
    x, _, y = text.partition(",")
    return int(x), int(y)


def parse_line(text: str) -> Line:
    left_pt, _, right_pt = text.partition(" -> ")
    return parse_point(left_pt), parse_point(right_pt)


def only_axis_aligned_lines(lines: Iterable[Line]) -> Generator[Line, None, None]:
    yield from filter(lambda line: line[0][0] == line[1][0] or line[0][1] == line[1][1], lines)


def points_covered_by_line(line: Line) -> set[Point]:
    xs: Iterable[int]
    ys: Iterable[int]

    if line[0][0] == line[1][0]:
        # Aligned with axis X.
        # Ensure that the 2nd point's y coord. is bigger
        if line[0][1] > line[1][1]:
            line = line[1], line[0]

        xs = cycle((line[0][0], ))
        ys = range(line[0][1], line[1][1] + 1)

    elif line[0][1] == line[1][1]:
        # Aligned with axis Y
        # Ensure that 2nd point's x coord. is bigger
        if line[0][0] > line[1][0]:
            line = line[1], line[0]

        xs = range(line[0][0], line[1][0] + 1)
        ys = cycle((line[0][1], ))

    else:
        raise RuntimeError("unaligned lines are not supported")

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
    lines = only_axis_aligned_lines(parse_line(line.strip()) for line in input)
    result = count_overlaps(lines)
    print(result)


if __name__ == "__main__":
    main()
