from fileinput import FileInput
from typing import Counter

from core import split_on, empty_str
from day14a import parse_inertions


def perform_insertions(pairs: Counter[str], table: dict[str, str]) -> Counter[str]:
    new_pairs: Counter[str] = Counter()

    for pair, n in pairs.items():
        insert = table[pair]
        new_pairs[pair[0] + insert] += n
        new_pairs[insert + pair[1]] += n

    return new_pairs


def initial_pair_count(template: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for a, b in zip(template[:-1], template[1:]):
        c[a + b] += 1
    return c


def pair_count_to_chr_counter(pairs: Counter[str]) -> Counter[str]:
    chars: Counter[str] = Counter()
    for (a, b), n in pairs.items():
        chars[a] += n
        chars[b] += n
    for c, n in chars.items():
        chars[c] = n // 2
    return chars


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    templates, insertion_pairs = split_on((i.strip() for i in input), empty_str)
    assert len(templates) == 1
    template = templates[0]
    table = parse_inertions(insertion_pairs)

    pair_counter = initial_pair_count(template)

    for _ in range(40):
        pair_counter = perform_insertions(pair_counter, table)

    counted = pair_count_to_chr_counter(pair_counter).most_common()
    most_common = counted[0]
    least_common = counted[-1]

    # No fucking clue why I have to add one, but it works
    print(most_common[1] - least_common[1] + 1)
