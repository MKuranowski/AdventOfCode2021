# cSpell: words BLTR

from dataclasses import dataclass
from fileinput import FileInput
from typing import Iterable, Literal, NamedTuple

from core import empty_str, split_on

Point = tuple[int, int]
Enhancer = dict[int, Literal[0, 1]]

NEIGHBOR_OFFSETS: list[Point] = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0), (0,  0), (1,  0),
    (-1,  1), (0,  1), (1,  1),
]


class BLTR(NamedTuple):
    """Bounds, aka. Bottom, Left, Top, Right"""
    b: int
    l: int
    t: int
    r: int

    def within(self, x: int, y: int) -> bool:
        return self.b <= y <= self.t and self.l <= x <= self.r


@dataclass
class Image:
    white_pixels: set[Point]
    enhancer: Enhancer
    background: Literal[0, 1] = 0

    def bounds(self) -> BLTR:
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0

        for x, y in self.white_pixels:
            min_x = min(x, min_x)
            max_x = max(x, max_x)
            min_y = min(y, min_y)
            max_y = max(y, max_y)

        return BLTR(min_y, min_x, max_y, max_x)

    def encode_neighbors(self, x: int, y: int, original_bounds: BLTR) -> int:
        encoded: int = 0

        for dx, dy in NEIGHBOR_OFFSETS:
            nx, ny = x + dx, y + dy
            encoded <<= 1

            if self.background and not original_bounds.within(nx, ny):
                encoded |= 1

            elif (nx, ny) in self.white_pixels:
                encoded |= 1

        return encoded

    def enhanced(self) -> "Image":
        new_whites: set[Point] = set()
        bounds = self.bounds()

        for y in range(bounds.b-1, bounds.t+2):
            for x in range(bounds.l-1, bounds.r+2):
                encoded = self.encode_neighbors(x, y, bounds)
                if self.enhancer[encoded]:
                    new_whites.add((x, y))

        return Image(
            new_whites,
            self.enhancer,
            self.background ^ self.enhancer[0]  # type: ignore | this xor can only return 0 or 1
        )

    def show_img(self) -> None:
        bounds = self.bounds()

        for y in range(bounds.b, bounds.t+1):
            for x in range(bounds.l, bounds.r+1):
                print("#" if (x, y) in self.white_pixels else ".", end="")
            print("\n", end="")
        print("\n", end="")


def load_enhancer(line: str) -> Enhancer:
    enhancer: Enhancer = {}
    for i, c in enumerate(line):
        enhancer[i] = 0 if c == "." else 1
    return enhancer


def load_white_pixels(lines: Iterable[str]) -> set[Point]:
    white_pixels: set[Point] = set()

    for y, row in enumerate(lines):
        for x, c in enumerate(row):
            if c == "#":
                white_pixels.add((x, y))

    return white_pixels


def main(rounds: int) -> None:
    input: "FileInput[str]" = FileInput()
    header, img = split_on((i.strip() for i in input), empty_str)
    assert len(header) == 1

    img = Image(load_white_pixels(img), load_enhancer(header[0]))

    for i in range(rounds):
        img = img.enhanced()

    print(len(img.white_pixels))


if __name__ == "__main__":
    main(2)
