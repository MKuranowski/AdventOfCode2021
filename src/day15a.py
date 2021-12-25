import dataclasses
import heapq
import math
from fileinput import FileInput
from typing import Iterable

Point = tuple[int, int]
Map = list[list[int]]


NEIGHBOR_DELTAS: list[Point] = [(0, 1), (1, 0), (0, -1), (-1, 0)]


@dataclasses.dataclass(order=True)
class AStarQueueItem:
    pt: Point = dataclasses.field(compare=False)
    cost_to: float = dataclasses.field(compare=False)
    heuristic: float = dataclasses.field(compare=True)


def dist(p1: Point, p2: Point) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[0]
    return (dx ** 2 + dy ** 2) ** 0.5


def valid_point(x: int, y: int, size: int) -> bool:
    return 0 <= x < size and 0 <= y < size


def neighbors(x: int, y: int, size: int) -> Iterable[Point]:
    for dx, dy in NEIGHBOR_DELTAS:
        nx = x + dx
        ny = y + dy
        if valid_point(nx, ny, size):
            yield nx, ny


def restore_path(pt: Point, came_from: dict[Point, Point]) -> list[Point]:
    path: list[Point] = [pt]
    while pt in came_from:
        pt = came_from[pt]
        path.insert(0, pt)
    return path


def a_star(start: Point, end: Point, map: Map, size: int) -> list[Point]:
    assert valid_point(*start, size)
    assert valid_point(*end, size)

    queue: list[AStarQueueItem] = [AStarQueueItem(start, 0, dist(start, end))]
    scores: dict[Point, float] = {start: 0}
    came_from: dict[Point, Point] = {}

    while queue:
        item = heapq.heappop(queue)
        if item.pt == end:
            return restore_path(item.pt, came_from)

        for neighbor in neighbors(*item.pt, size):
            new_cost_to = item.cost_to + map[neighbor[0]][neighbor[1]]

            if new_cost_to < scores.get(neighbor, math.inf):
                scores[neighbor] = new_cost_to
                came_from[neighbor] = item.pt
                heapq.heappush(
                    queue,
                    AStarQueueItem(
                        neighbor,
                        new_cost_to,
                        new_cost_to + dist(neighbor, end),
                    ),
                )

    raise ValueError("no path found")


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    map: Map = [[int(cell) for cell in line.strip()] for line in input]
    size = len(map)  # maps are square
    path = a_star((0, 0), (size-1, size-1), map, size)
    result = sum(map[x][y] for x, y in path) - map[0][0]
    print(result)
