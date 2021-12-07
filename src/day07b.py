from fileinput import FileInput
from typing import Iterable

import day07a


def single_fuel_needed(delta: int) -> int:
    return delta * (delta + 1) // 2


def calculate_fuel_needed(positions: Iterable[int], target: int) -> int:
    return sum(single_fuel_needed(abs(target - position)) for position in positions)


if __name__ == "__main__":
    day07a.calculate_fuel_needed = calculate_fuel_needed

    input: "FileInput[str]" = FileInput()
    initial_positions = list(map(int, next(input).rstrip().split(",")))
    print(day07a.find_cheapest_position(initial_positions))
