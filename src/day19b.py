from fileinput import FileInput
from itertools import combinations

from day19a import load_scanners, match_for

# See stderr output from part A - this is a hint which Scanner to match next.
# Otherwise we have to wait for the brute-force to complete.

# For testing dataset
# MATCH_ORDER = [1, 3, 4, 2]

# For normal dataset
MATCH_ORDER = [
    4, 19, 10, 18, 1, 5, 8, 17, 13, 2, 6, 7, 9, 20, 21, 22, 25, 14, 23,
    16, 11, 26, 3, 27, 28, 29, 15, 30, 31, 32, 33, 34, 12, 35, 36, 24
]


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    matched, unmatched = load_scanners(input)

    for match_id in MATCH_ORDER:
        match_for(matched, unmatched, unmatched[match_id])

    assert not unmatched

    max_dist: int = -1

    for s1, s2 in combinations(matched.values(), 2):
        assert s1.position is not None
        assert s2.position is not None
        dist = (s2.position - s1.position).manhattan_dist()
        if dist > max_dist:
            max_dist = dist

    print(max_dist)
