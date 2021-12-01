import fileinput
from day01a import count_increases


def sum_windows(samples: list[float]) -> list[float]:
    return [sum(window) for window in zip(samples[:-2], samples[1:-1], samples[2:])]


if __name__ == "__main__":
    windows = sum_windows([int(line) for line in fileinput.input()])
    result = count_increases(windows)
    print(result)
