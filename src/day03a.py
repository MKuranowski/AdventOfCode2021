import fileinput
from math import log2


def get_rates(numbers: list[int]) -> tuple[int, int]:
    gamma_rate = 0
    msb = int(log2(max(numbers)))
    mask = 1 << msb

    while mask:
        ones_count = sum(1 for num in numbers if num & mask)
        if ones_count > len(numbers)//2:
            gamma_rate |= mask
        mask >>= 1

    epsilon_rate = gamma_rate ^ ((1 << (msb + 1)) - 1)
    return gamma_rate, epsilon_rate


if __name__ == "__main__":
    gamma_rate, epsilon_rate = get_rates([int(line, 2) for line in fileinput.input()])
    print(gamma_rate * epsilon_rate)
