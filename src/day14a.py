from fileinput import FileInput
from typing import Counter, Iterable

from core import split_on, empty_str


def parse_inertions(lines: Iterable[str]) -> dict[str, str]:
    insertions: dict[str, str] = {}

    for line in lines:
        left, _, right = line.partition(" -> ")
        assert len(left) == 2
        assert len(right) == 1

        insertions[left] = right

    return insertions


def perform_insertions(value: str, table: dict[str, str]) -> str:
    i = 0

    while i < len(value) - 1:
        insert = table[value[i:i+2]]
        value = value[:i+1] + insert + value[i+1:]
        i += 2

    return value


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    values, insertion_pairs = split_on((i.strip() for i in input), empty_str)
    assert len(values) == 1
    value = values[0]
    table = parse_inertions(insertion_pairs)

    for _ in range(10):
        value = perform_insertions(value, table)

    counted = Counter(value).most_common()
    most_common = counted[0]
    least_common = counted[-1]

    print(most_common[1] - least_common[1])
