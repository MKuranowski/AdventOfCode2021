from math import log2
import fileinput


def get_rating(numbers: list[int], follow_most_common: bool = True) -> int:
    # Start from the MSB
    # bit_idx = int(log2(max(numbers)))
    mask = 1 << int(log2(max(numbers)))

    while len(numbers) > 1:
        assert mask, "multiple matching numbers"
        # Split numbers into 2 bins, depending on the nth bit of the number
        with_one: list[int] = []
        with_zero: list[int] = []

        for num in numbers:
            (with_one if num & mask else with_zero).append(num)

        if follow_most_common:
            numbers = with_one if len(with_one) >= len(with_zero) else with_zero
        else:
            numbers = with_zero if len(with_one) >= len(with_zero) else with_one

        # Shift the mask
        mask >>= 1

    assert numbers
    return numbers[0]


if __name__ == "__main__":
    numbers = [int(line, 2) for line in fileinput.input()]
    oxygen_rate = get_rating(numbers, True)
    co2_rate = get_rating(numbers, False)
    print(oxygen_rate * co2_rate)
