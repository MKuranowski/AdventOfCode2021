# cSpell: words nlargest
import operator
from fileinput import FileInput
from functools import reduce
from heapq import nlargest
from typing import Iterable

from day09a import Point, find_low_points, load_heightmap, neighbors


def expand_basin(low_point: Point, map: list[list[int]], height: int, width: int) -> set[Point]:
    basin: set[Point] = set()
    to_expand: set[Point] = {low_point}

    while to_expand:
        point = to_expand.pop()
        basin.add(point)

        for neighbor in neighbors(point, height, width):
            nv = map[neighbor[0]][neighbor[1]]
            if nv != 9 and neighbor not in basin:
                to_expand.add(neighbor)

    return basin


def basin_sizes(map: list[list[int]], height: int, width: int) -> Iterable[int]:
    for low_point, _ in find_low_points(map, height, width):
        yield len(expand_basin(low_point, map, height, width))


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    heightmap = load_heightmap(input)
    height = len(heightmap)
    width = len(heightmap[0])

    largest_3_basins = nlargest(3, basin_sizes(heightmap, height, width))
    print(reduce(operator.mul, largest_3_basins))
