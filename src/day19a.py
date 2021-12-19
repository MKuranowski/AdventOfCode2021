import re
import sys
from collections import Counter
from dataclasses import dataclass
from fileinput import FileInput
from itertools import product
from typing import Iterable, NamedTuple, Optional

from core import empty_str, split_on


def sgn(x: int) -> int:
    return 1 if x >= 0 else -1


class Vec3D(NamedTuple):
    x: int
    y: int
    z: int

    def __eq__(self, other: "Vec3D") -> bool:
        return all(i == j for i, j in zip(self, other))

    def __neq__(self, other: "Vec3D") -> bool:
        return any(i != j for i, j in zip(self, other))

    def __add__(self, other: "Vec3D") -> "Vec3D":
        return Vec3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3D") -> "Vec3D":
        return Vec3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> "Vec3D":
        return Vec3D(-self.x, -self.y, -self.z)

    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def manhattan_dist(self) -> int:
        return sum(abs(i) for i in self)

    def flipped(self, flip_axis: int) -> "Vec3D":
        return Vec3D(
            (-self.x if (flip_axis & 1) else self.x),
            (-self.y if (flip_axis & 2) else self.y),
            (-self.z if (flip_axis & 4) else self.z),
        )

    def swapped(self, swap_id: int) -> "Vec3D":
        match swap_id:
            case 0:
                return self
            case 1:
                return Vec3D(self.x, self.z, self.y)
            case 2:
                return Vec3D(self.y, self.x, self.z)
            case 3:
                return Vec3D(self.y, self.z, self.x)
            case 4:
                return Vec3D(self.z, self.x, self.y)
            case 5:
                return Vec3D(self.z, self.y, self.x)
            case _:
                raise ValueError(f"invalid swap_id: {swap_id}")


BeaconRelative = Vec3D
BeaconAbsolute = Vec3D

MATCH_THRESHOLD = 12


@dataclass
class Scanner:
    id: int
    beacons: set[BeaconRelative]
    position: Optional[Vec3D] = None

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> "Scanner":
        i = iter(lines)
        header_match = re.match(r"^--- scanner (\d+) ---$", next(i))
        assert header_match

        self = cls(int(header_match[1]), set(), Vec3D(0, 0, 0) if header_match[1] == "0" else None)
        for line in i:
            self.beacons.add(Vec3D(*map(int, line.split(","))))
        return self

    def flip(self, flip_axis: int) -> "Scanner":
        return Scanner(
            self.id,
            {i.flipped(flip_axis) for i in self.beacons},
            self.position
        )

    def swap(self, swap_id: int) -> "Scanner":
        return Scanner(
            self.id,
            {i.swapped(swap_id) for i in self.beacons},
            self.position
        )

    def beacons_absolute(self) -> set[BeaconAbsolute]:
        assert self.position is not None
        return {i + self.position for i in self.beacons}

    def find_matching_offset(self, other: "Scanner") -> Optional[Vec3D]:
        assert self.position is not None
        offset_counter: Counter[Vec3D] = Counter()

        for left_beacon, right_beacon in product(self.beacons, other.beacons):
            # Assume both match up
            offset = -(right_beacon - left_beacon)
            offset_counter[offset] += 1
            other.position = self.position + offset

            if offset_counter[offset] >= MATCH_THRESHOLD:
                return offset

            other.position = None

    def find_match_by_transforming(self, other: "Scanner") -> Optional["Scanner"]:
        for flip_axis, swap_id in product(range(8), range(6)):
            transformed = other.flip(flip_axis).swap(swap_id)
            if self.find_matching_offset(transformed) is not None:
                return transformed


def load_scanners(input: Iterable[str]) -> tuple[dict[int, Scanner], dict[int, Scanner]]:
    scanners: dict[int, Scanner] = {}
    for lines in split_on((i.strip() for i in input), empty_str):
        scanner = Scanner.from_lines(lines)
        scanners[scanner.id] = scanner

    matched_scanners: dict[int, Scanner] = {0: scanners.pop(0)}
    return matched_scanners, scanners


def match_for(matched: dict[int, Scanner], unmatched: dict[int, Scanner],
              find_for: Scanner) -> bool:
    for try_match in matched.values():
        find_for_transformed = try_match.find_match_by_transforming(find_for)

        if find_for_transformed:
            unmatched.pop(find_for.id)
            matched[find_for.id] = find_for_transformed
            print(
                f"Matched {find_for.id} ({len(matched) / (len(unmatched)+len(matched)):.2%})",
                file=sys.stderr,
            )
            return True
    return False


def match_next(matched: dict[int, Scanner], unmatched: dict[int, Scanner]) -> None:
    for find_for in unmatched.values():
        if match_for(matched, unmatched, find_for):
            return

    raise ValueError("no more matches")


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    matched, unmatched = load_scanners(input)

    while unmatched:
        match_next(matched, unmatched)

    all_bacons: set[BeaconAbsolute] = set()

    for scanner in matched.values():
        all_bacons.update(scanner.beacons_absolute())

    print(len(all_bacons))
