from fileinput import FileInput
from typing import Iterable

from core import empty_str, split_on

Point = tuple[int, int]  # x, y
Fold = tuple[int, int]   # fold_axis, along
Points = set[Point]


def parse_points(lines: Iterable[str]) -> Points:
    points: Points = set()
    for line in lines:
        x, _, y = line.partition(",")
        points.add((int(x), int(y)))
    return points


def parse_folds(lines: Iterable[str]) -> list[Fold]:
    folds: list[Fold] = []
    for line in lines:
        axis, _, along = line.rpartition(" ")[2].partition("=")
        folds.append((0 if axis == "x" else 1, int(along)))
    return folds


def partition_for_fold(points: Points, fold_axis: int, along: int) -> tuple[Points, Points]:
    # Split the set of points into 2 buckets:
    # 1. points before the fold line and after the fold line
    before_fold: Points = set()
    after_fold: Points = set()

    for point in points:
        if point[fold_axis] < along:
            before_fold.add(point)
        elif point[fold_axis] > along:
            after_fold.add(point)
        # Dropping all points on the fold axis

    return before_fold, after_fold


def mirror_point(point: Point, fold_axis: int, along: int) -> Point:
    if fold_axis == 0:
        return 2*along - point[0], point[1]
    else:
        return point[0], 2*along - point[1]


def perform_fold(points: Points, fold_axis: int, along: int) -> Points:
    correct, to_mirror = partition_for_fold(points, fold_axis, along)

    for point in to_mirror:
        correct.add(mirror_point(point, fold_axis, along))

    return correct


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    point_lines, fold_lines = split_on((i.strip() for i in input), empty_str)

    points = parse_points(point_lines)
    folds = parse_folds(fold_lines)

    # Perform a single fold
    points = perform_fold(points, *folds[0])
    print(len(points))
