import fileinput


def count_increases(samples: list[float]) -> int:
    return sum(
        1
        for a, b in zip(samples[:-1], samples[1:])
        if b > a
    )


if __name__ == "__main__":
    result = count_increases([int(line) for line in fileinput.input()])
    print(result)
