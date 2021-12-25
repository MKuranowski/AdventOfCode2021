import enum
from dataclasses import dataclass, field
from heapq import heappop, heappush
from fileinput import FileInput
from math import inf
from typing import Iterable, NamedTuple, Optional


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
    """State represents a burrow after n moves were performed.
    To solve the challenge, we'll want to find the end state with the lowest energy.
    """
    burrow: Burrow = field(compare=False)
    energy: int = field(default=0, compare=True)

    def __hash__(self) -> int:
        return hash((self.burrow, self.energy))

    def is_end(self) -> bool:
        for room_idx in range(ROOMS):
            for room_spot in range(ROOM_SIZE):
                if self.burrow.rooms[room_idx][room_spot] != room_idx:
                    return False

        assert all(s == Spot.Empty for s in self.burrow.hallway)
        return True

    def can_move_from_spot_to_room(self, hallway_idx: int, room_idx: int) -> bool:
        """Checks if the path from the hallway spot to a room
        is not obstructed by any other amphipod."""
        left = hallway_idx + 1
        right = room_idx + 2
        if left > right:
            spots = self.burrow.hallway[right:left-1]
        else:
            spots = self.burrow.hallway[left:right]

        return all(spot == Spot.Empty for spot in spots)

    def can_move_into_room(self, room_idx: int) -> Optional[int]:
        """Checks if the amphipod can move into a room.
        An amphipod can move into a room if there's an empty spot,
        and any other amphipods below (towards the "window") are the expected/valid
        amphipods.

        Returns None if the move can't be performed, and a room_spot_idx otherwise.
        """
        for room_spot_idx in range(ROOM_SIZE):
            occupant = self.burrow.rooms[room_idx][room_spot_idx]

            if occupant == Spot.Empty:
                return room_spot_idx

            elif occupant != room_idx:
                return None

    def can_move_from_room(self, room_idx: int) -> Optional[int]:
        """Checks if anyone from the given room should move.

        Returns room_spot_idx of the amphipod to move, as long
        as it's in the incorrect room, or any amphipods below are also in
        the incorrect room.
        """
        room = self.burrow.rooms[room_idx]

        # Empty room - nothing to move from
        if room[0] == Spot.Empty:
            return None

        # Check if room is "valid" - it contains only valid amphipods or empty spots
        # => no need to move in this case
        if all(s == Spot.Empty or s == room_idx for s in room):
            return None

        # Find the top item
        for idx in range(ROOM_SIZE):
            if room[idx] == Spot.Empty:
                return idx-1

        return ROOM_SIZE - 1

    def possible_moves(self) -> Iterable["State"]:
        """Generates all of the possible moves from the current state -
        first generating all moves **to** a room, and then by
        generating moves **from** all rooms.
        """
        # First check if someone from the hallway can move to its room
        for idx in range(HALLWAY_LENGTH):
            amphipod = self.burrow.hallway[idx]

            # Check if there's an amphipod at this idx and
            # it has a free path to its room
            if amphipod != Spot.Empty and self.can_move_from_spot_to_room(idx, amphipod) \
                    and (insert_into_spot := self.can_move_into_room(amphipod)) is not None:

                energy_delta = abs(unwrap_hallway_index(idx) - 2 * (amphipod + 1))
                energy_delta += ROOM_SIZE - insert_into_spot
                energy_delta *= amphipod.energy_multiplier()

                yield State(
                    self.burrow.to_room(idx, amphipod, insert_into_spot),
                    self.energy + energy_delta
                )

        # Then, check possible moves into the hallway
        for room_idx in range(ROOMS):
            from_spot = self.can_move_from_room(room_idx)

            if from_spot is None:
                continue

            amphipod = self.burrow.rooms[room_idx][from_spot]

            # Generate all possible spots to move to
            for hallway_idx in range(HALLWAY_LENGTH):
                if self.burrow.hallway[hallway_idx] != Spot.Empty \
                        or not self.can_move_from_spot_to_room(hallway_idx, room_idx):
                    continue

                energy_delta = abs(unwrap_hallway_index(hallway_idx) - 2 * (room_idx + 1))
                energy_delta += ROOM_SIZE - from_spot
                energy_delta *= amphipod.energy_multiplier()

                yield State(
                    self.burrow.to_hallway(hallway_idx, room_idx, from_spot),
                    self.energy + energy_delta
                )


def find_cheapest(initial_state: State) -> State:
    """Uses Dijkstra's algorithm to find the least-energy
    solved state.

    Because we don't care about the specific steps towards a solution,
    there's no need to keep track of the `prev`/`came_from` mapping.

    It takes a few seconds to find the solution, I wonder if
    it can be improved by switching to A*; or maybe it's possible to solve
    the task in an entirely different way...
    """
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
