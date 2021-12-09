from fileinput import FileInput
from typing import Iterable

Point = tuple[int, int]


def maybe_neighbors(pt: Point) -> Iterable[Point]:
    yield pt[0] - 1, pt[1]
    yield pt[0] + 1, pt[1]
    yield pt[0], pt[1] - 1
    yield pt[0], pt[1] + 1


def neighbors(pt: Point, height: int, width: int) -> Iterable[Point]:
    for x, y in maybe_neighbors(pt):
        if 0 <= x < height and 0 <= y < width:
            yield x, y


def find_low_points(heightmap: list[list[int]], height: int, width: int) \
        -> Iterable[tuple[Point, int]]:
    for x, row in enumerate(heightmap):
        for y, value in enumerate(row):
            if all(heightmap[nx][ny] > value for nx, ny in neighbors((x, y), height, width)):
                yield (x, y), value


def load_heightmap(lines: Iterable[str]) -> list[list[int]]:
    return [[int(chr) for chr in line.strip()] for line in lines]


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    heightmap = load_heightmap(input)
    height = len(heightmap)
    width = len(heightmap[0])
    risk_level_of_low_points = sum(
        1 + value for _, value in find_low_points(heightmap, height, width)
    )
    print(risk_level_of_low_points)
