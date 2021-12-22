from fileinput import FileInput
from typing import NamedTuple
from itertools import combinations
import sys

# This is a stupid solution, it takes 10 minutes to run


def parse_range(r: str) -> frozenset[int]:
    left, _, right = r.partition("..")
    return frozenset(range(int(left), int(right)+1))


def ensure_continuity(r: frozenset[int]) -> tuple[frozenset[int], frozenset[int]]:
    if not r:
        return frozenset(), frozenset()

    before: set[int] = set()
    after: set[int] = set()

    r_sorted = sorted(r)
    to_after = False

    before.add(r_sorted[0])

    for left, right in zip(r_sorted[:-1], r_sorted[1:]):
        to_after = to_after or right - left > 1

        if to_after:
            after.add(right)

        else:
            before.add(right)

    return frozenset(before), frozenset(after)


class Cube(NamedTuple):
    xs: frozenset[int]
    ys: frozenset[int]
    zs: frozenset[int]

    @classmethod
    def from_str(cls, cube_str: str) -> "Cube":
        x_str, y_str, z_str = cube_str.split(",")
        xs = parse_range(x_str[2:])
        ys = parse_range(y_str[2:])
        zs = parse_range(z_str[2:])
        return cls(xs, ys, zs)

    def __len__(self) -> int:
        return len(self.xs) * len(self.ys) * len(self.zs)

    def intersects(self, other: "Cube") -> bool:
        return bool((self.xs & other.xs) and (self.ys & other.ys) and (self.zs & other.zs))

    def chomp(self, other: "Cube") -> set["Cube"]:
        overlap_xs = self.xs & other.xs
        overlap_ys = self.ys & other.ys
        overlap_zs = self.zs & other.zs

        if len(overlap_xs) == 0 or len(overlap_ys) == 0 or len(overlap_zs) == 0:
            return {self}

        nonoverlap_xs, leftover_xs = ensure_continuity(self.xs - other.xs)
        nonoverlap_ys, leftover_ys = ensure_continuity(self.ys - other.ys)
        nonoverlap_zs, leftover_zs = ensure_continuity(self.zs - other.zs)

        if leftover_xs:
            return Cube(nonoverlap_xs | overlap_xs, self.ys, self.zs).chomp(other) \
                | {Cube(leftover_xs, self.ys, self.zs)}

        if leftover_ys:
            return Cube(self.xs, nonoverlap_ys | overlap_ys, self.zs).chomp(other) \
                | {Cube(self.xs, leftover_ys, self.zs)}

        if leftover_zs:
            return Cube(self.xs, self.ys, nonoverlap_zs | overlap_zs).chomp(other) \
                | {Cube(self.xs, self.ys, leftover_zs)}

        c1 = Cube(self.xs, self.ys, nonoverlap_zs)
        c2 = Cube(nonoverlap_xs, self.ys, overlap_zs)
        c3 = Cube(overlap_xs, nonoverlap_ys, overlap_zs)
        return {c for c in (c1, c2, c3) if len(c) > 0}


def reactor_on(r: set[Cube], new: Cube) -> set[Cube]:
    new_set = {new}

    for c1 in r:
        tmp: set[Cube] = set()
        for c2 in new_set:
            x = c2.chomp(c1)
            # assert_no_overlaps(x)
            tmp.update(x)
        # assert_no_overlaps(tmp)
        new_set = tmp

    return r | new_set


def reactor_off(r: set[Cube], rem: Cube) -> set[Cube]:
    new: set[Cube] = set()
    for c in r:
        new.update(c.chomp(rem))
    return new


def process_line(r: set[Cube], line: str) -> set[Cube]:
    status, _, cube_str = line.partition(" ")
    cube = Cube.from_str(cube_str)

    if status == "on":
        return reactor_on(r, cube)
    elif status == "off":
        return reactor_off(r, cube)
    else:
        raise ValueError(f"unknown status: {status!r} ({line!r})")


def assert_no_overlaps(r: set[Cube]) -> None:
    for a, b in combinations(r, 2):
        assert not a.intersects(b)


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    lines = filter(None, (i.strip() for i in input))
    reactor: set[Cube] = set()

    for idx, line in enumerate(lines):
        print(idx, repr(line), file=sys.stderr)
        reactor = process_line(reactor, line.strip())
        # assert_no_overlaps(reactor)

    print(sum(len(c) for c in reactor))
