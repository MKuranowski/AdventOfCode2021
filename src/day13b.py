from fileinput import FileInput

from core import empty_str, split_on
from day13a import Points, parse_folds, parse_points, perform_fold


def pprint_points(points: Points) -> str:
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    text: str = ""

    for y in range(max_y+1):
        for x in range(max_x+1):
            text += "#" if (x, y) in points else " "
        text += "\n"

    return text


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    point_lines, fold_lines = split_on((i.strip() for i in input), empty_str)

    points = parse_points(point_lines)
    folds = parse_folds(fold_lines)

    # Perform folds
    for fold in folds:
        points = perform_fold(points, *fold)

    print(pprint_points(points))
