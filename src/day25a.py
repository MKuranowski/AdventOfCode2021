from dataclasses import dataclass
from fileinput import FileInput
from typing import Iterable

Point = tuple[int, int]


@dataclass
class SeaFloor:
    width: int
    height: int

    east_cucumbers: set[Point]
    south_cucumbers: set[Point]

    @classmethod
    def from_input(cls, lines: Iterable[str]) -> "SeaFloor":
        self = cls(0, 0, set(), set())

        for y, line in enumerate(lines):
            # Update sea floor dimensions
            self.height += 1
            if self.width:
                assert len(line) == self.width
            else:
                self.width = len(line)

            # Add cucumbers
            for x, c in enumerate(line):
                match c:
                    case ">":
                        self.east_cucumbers.add((x, y))
                    case "v":
                        self.south_cucumbers.add((x, y))

        return self

    def move_east(self, cucumber: Point) -> tuple[Point, bool]:
        moved: Point = (cucumber[0] + 1) % self.width, cucumber[1]

        if moved in self.east_cucumbers or moved in self.south_cucumbers:
            return cucumber, False
        else:
            return moved, True

    def move_south(self, cucumber: Point) -> tuple[Point, bool]:
        moved: Point = cucumber[0], (cucumber[1] + 1) % self.height

        if moved in self.east_cucumbers or moved in self.south_cucumbers:
            return cucumber, False
        else:
            return moved, True

    def move_all_east(self) -> int:
        move_count: int = 0
        new_east: set[Point] = set()

        for cucumber in self.east_cucumbers:
            new_cucumber, did_move = self.move_east(cucumber)
            new_east.add(new_cucumber)
            move_count += int(did_move)

        self.east_cucumbers = new_east
        return move_count

    def move_all_south(self) -> int:
        move_count: int = 0
        new_south: set[Point] = set()

        for cucumber in self.south_cucumbers:
            new_cucumber, did_move = self.move_south(cucumber)
            new_south.add(new_cucumber)
            move_count += int(did_move)

        self.south_cucumbers = new_south
        return move_count

    def move_all(self) -> int:
        count = self.move_all_east()
        count += self.move_all_south()
        return count


if __name__ == "__main__":
    sea_floor = SeaFloor.from_input(i.strip() for i in FileInput())
    moves = 1
    while sea_floor.move_all():
        moves += 1
    print(moves)
