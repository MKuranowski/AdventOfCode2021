import enum
from dataclasses import dataclass, field
from heapq import heappop, heappush
from fileinput import FileInput
from math import inf
from typing import Iterable, NamedTuple


HALLWAY_LENGTH = 7
ROOMS = 4
ROOM_SIZE = 2


class Spot(enum.IntEnum):
    Empty = -1
    A = 0
    B = 1
    C = 2
    D = 3

    def energy_multiplier(self) -> int:
        assert self != Spot.Empty
        return 10 ** self

    @classmethod
    def from_str(cls, x: str) -> "Spot":
        match x:
            case ".":
                return Spot.Empty
            case "A":
                return Spot.A
            case "B":
                return Spot.B
            case "C":
                return Spot.C
            case "D":
                return Spot.D
            case _:
                raise ValueError("Invalid spot string: ", x)

    def __str__(self) -> str:
        match self:
            case Spot.Empty:
                return "."
            case Spot.A:
                return "A"
            case Spot.B:
                return "B"
            case Spot.C:
                return "C"
            case Spot.D:
                return "D"
        raise RuntimeError("unreachable")


# Memory layout of the Burrow implementation
#
# Hn == hallway[n] - represents a spot in the hallway, which can be occupied by an amphipod
# Un == unwrapped_hallway[n] - only used in distance calculation, never stored actually
#
#  U0  U1  U2   U3  U4   U5  U6   U7  U8   U9  U10
#  H0  H1  ___  H2  ___  H3  ___  H4  ___  H5  H6
#          R01      R11      R21      R31
#          R00      R10      R20      R30
#
# In handsight, it would probably be better to store spots within the room,
# in the opposite order, so that `room[i][0]` is the hallway spot.
#
# The 'Spot' enum is designed in such a way, that an amphipod (= non-empty spot)
# wants to be in the same room as its value; in other words, given an amphipod,
# it wants to go to rooms[that_amphipod].


def unwrap_hallway_index(i: int) -> int:
    if i <= 1:
        return i
    elif i <= 5:
        return 2*i - 1
    else:
        return i + 4


class Burrow(NamedTuple):
    hallway: list[Spot]
    rooms: list[list[Spot]]

    def __hash__(self) -> int:
        return hash((
            tuple(self.hallway),
            tuple(tuple(room) for room in self.rooms)
        ))

    @classmethod
    def from_input(cls, lines: Iterable[str]) -> "Burrow":
        iterator = iter(lines)
        next(iterator)  # Ignore the top border
        next(iterator)  # Ignore the hallway, as it's initially empty

        hallway: list[Spot] = [Spot.Empty] * HALLWAY_LENGTH
        rooms: list[list[Spot]] = [[Spot.Empty] * ROOM_SIZE for _ in range(ROOMS)]

        for room_spot in range(ROOM_SIZE-1, -1, -1):
            line = next(iterator)

            for room_idx in range(ROOMS):
                # Find the char in the line representing the spot;
                # + 3to offset initial border, times 2 to skip borders between rooms
                char = line[3 + 2 * room_idx]
                assert char in {"A", "B", "C", "D"}
                rooms[room_idx][room_spot] = Spot.from_str(char)

        return cls(hallway, rooms)

    def _hallway_str(self) -> str:
        strings = ["."] * (HALLWAY_LENGTH + ROOMS)
        for i, spot in enumerate(self.hallway):
            strings[unwrap_hallway_index(i)] = str(spot)
        return "".join(strings)

    def __str__(self) -> str:
        width = HALLWAY_LENGTH + ROOMS
        rows: list[str] = ["#" * (width + 2)]

        # Add the hallway
        rows.append("#" + self._hallway_str() + "#")

        # Add the rooms
        for i in range(ROOM_SIZE-1, -1, -1):
            room = "#".join(str(self.rooms[j][i]) for j in range(ROOMS))

            if i == ROOM_SIZE-1:
                rows.append("###" + room + "###")
            else:
                rows.append("  #" + room + "#  ")

        # Add the bottom border
        rows.append("  " + "#" * (width - 2) + "  ")
        rows.append("")  # For a final newline
        return "\n".join(rows)

    def to_room(self, hallway_idx: int, room_idx: int, room_spot_idx: int) -> "Burrow":
        a = self.hallway[hallway_idx]

        assert a != Spot.Empty
        assert self.rooms[room_idx][room_spot_idx] == Spot.Empty
        if room_spot_idx == 0:
            assert self.rooms[room_idx][1] == Spot.Empty

        new_hallway = self.hallway.copy()
        new_hallway[hallway_idx] = Spot.Empty

        new_room = self.rooms[room_idx].copy()
        new_room[room_spot_idx] = a

        new_rooms = self.rooms.copy()
        new_rooms[room_idx] = new_room

        return Burrow(new_hallway, new_rooms)

    def to_hallway(self, hallway_idx: int, room_idx: int, room_spot_idx: int) -> "Burrow":
        a = self.rooms[room_idx][room_spot_idx]

        assert self.hallway[hallway_idx] == Spot.Empty
        assert a != Spot.Empty
        if room_spot_idx == 0:
            assert self.rooms[room_idx][1] == Spot.Empty

        new_hallway = self.hallway.copy()
        new_hallway[hallway_idx] = a

        new_room = self.rooms[room_idx].copy()
        new_room[room_spot_idx] = Spot.Empty

        new_rooms = self.rooms.copy()
        new_rooms[room_idx] = new_room

        return Burrow(new_hallway, new_rooms)


@dataclass(order=True)
class State:
    burrow: Burrow = field(compare=False)
    energy: int = field(default=0, compare=True)

    def __hash__(self) -> int:
        return hash((self.burrow, self.energy))

    def can_move_from_spot_to_room(self, a: int, b: int) -> bool:
        left = a + 1
        right = b + 2
        if left > right:
            spots = self.burrow.hallway[right:left-1]
        else:
            spots = self.burrow.hallway[left:right]

        return all(spot == Spot.Empty for spot in spots)

    def is_end(self) -> bool:
        for room_idx in range(ROOMS):
            if self.burrow.rooms[room_idx][0] != room_idx \
                    or self.burrow.rooms[room_idx][1] != room_idx:
                return False

        assert all(s == Spot.Empty for s in self.burrow.hallway)
        return True

    def possible_moves(self) -> Iterable["State"]:
        # First check if someone from the hallway can move to its room
        for idx in range(HALLWAY_LENGTH):
            amphipod = self.burrow.hallway[idx]

            # Check if there's an amphipod at this idx and
            # it has a free path to its room
            if amphipod != Spot.Empty and self.can_move_from_spot_to_room(idx, amphipod):

                # Move into an empty room
                if self.burrow.rooms[amphipod][0] == Spot.Empty:
                    # Calculate energy required for the move
                    distance_to_room = abs(unwrap_hallway_index(idx) - 2 * (amphipod + 1))
                    energy_delta = amphipod.energy_multiplier() * (2 + distance_to_room)
                    yield State(
                        self.burrow.to_room(idx, amphipod, 0),
                        self.energy + energy_delta
                    )

                # Move into a room where the "window" seat is occupied by the expected amphipod
                elif self.burrow.rooms[amphipod][0] == amphipod and \
                        self.burrow.rooms[amphipod][1] == Spot.Empty:
                    distance_to_room = abs(unwrap_hallway_index(idx) - 2 * (amphipod + 1))
                    energy_delta = amphipod.energy_multiplier() * (1 + distance_to_room)
                    yield State(
                        self.burrow.to_room(idx, amphipod, 1),
                        self.energy + energy_delta
                    )

        # Then, check possible moves into the hallway
        for room_idx in range(ROOMS):

            if self.burrow.rooms[room_idx][1] != Spot.Empty:
                # Try to move someone from the hallway spot
                amphipod = self.burrow.rooms[room_idx][1]
                window_amphipod = self.burrow.rooms[room_idx][0]
                from_spot = 1
                distance_onto_hallway = 1

                assert window_amphipod != Spot.Empty

                # Skip this step is the room is occupied by correct amphipod
                if amphipod == room_idx and window_amphipod == room_idx:
                    continue

            elif self.burrow.rooms[room_idx][0] != Spot.Empty:
                # Try to move someone from the window spot
                amphipod = self.burrow.rooms[room_idx][0]
                from_spot = 0
                distance_onto_hallway = 2

                # This is only required it the spot is occupied by the incorrect amphipod
                if amphipod == room_idx:
                    continue

            else:
                # No one to move
                continue

            # Generate all possible spots to move to
            for hallway_idx in range(HALLWAY_LENGTH):
                if self.burrow.hallway[hallway_idx] != Spot.Empty \
                        or not self.can_move_from_spot_to_room(hallway_idx, room_idx):
                    continue

                energy_delta = abs(unwrap_hallway_index(hallway_idx) - 2 * (room_idx + 1))
                energy_delta += distance_onto_hallway
                energy_delta *= amphipod.energy_multiplier()
                yield State(
                    self.burrow.to_hallway(hallway_idx, room_idx, from_spot),
                    self.energy + energy_delta
                )


def find_cheapest(initial_state: State) -> State:
    min_energies: dict[Burrow, float] = {initial_state.burrow: 0}
    queue: list[State] = [initial_state]

    while queue:
        state = heappop(queue)

        if state.is_end():
            return state

        for new_state in state.possible_moves():
            if new_state.energy < min_energies.get(new_state.burrow, inf):
                min_energies[new_state.burrow] = new_state.energy
                heappush(queue, new_state)

    raise RuntimeError("no solution found")


if __name__ == "__main__":
    initial_burrow = Burrow.from_input(FileInput())
    initial_state = State(initial_burrow)

    cheapest_end_state = find_cheapest(initial_state)
    print(cheapest_end_state.energy)
