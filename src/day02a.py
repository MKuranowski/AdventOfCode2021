from fileinput import FileInput
from typing import Iterable


def simulate(instructions: Iterable[str]) -> tuple[int, int]:
    x: int = 0
    y: int = 0

    for instruction in instructions:
        direction, value_str = instruction.split()
        value = int(value_str)

        if direction == "forward":
            x += value
        elif direction == "down":
            y += value
        elif direction == "up":
            y -= value
        else:
            raise ValueError("unknown direction: " + direction)

    return x, y


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    x, y = simulate(input)
    print(x * y)
