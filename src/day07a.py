from fileinput import FileInput
from typing import Iterable


def calculate_fuel_needed(positions: Iterable[int], target: int) -> int:
    return sum(abs(target - position) for position in positions)


def find_cheapest_position(positions: list[int]) -> int:
    bounds = range(min(positions), max(positions)+1)
    return min(calculate_fuel_needed(positions, bound) for bound in bounds)


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    initial_positions = list(map(int, next(input).rstrip().split(",")))
    print(find_cheapest_position(initial_positions))
