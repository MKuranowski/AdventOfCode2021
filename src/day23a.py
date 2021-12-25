import enum
from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import inf
from typing import Iterable, NamedTuple

# 0, 1 → to the left of room[0]
#    2 → between room[0] and room[1]
#    3 → between room[1] and room[2]
#    4 → between room[2] and room[3]
# 5, 6 → to the right of room[3]
HALLWAY_LENGTH = 7

# room[0] → outer ("window") spot
# room[1] → inner ("hallway") spot
ROOMS = 4


class Spot(enum.IntEnum):
    Empty = -1
    A = 0
    B = 1
    C = 2
    D = 3

    def energy_multiplier(self) -> int:
        assert self != Spot.Empty
        return 10 ** self

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
        raise RuntimeError()


class Burrow(NamedTuple):
    hallway: list[Spot]
    rooms: list[list[Spot]]

    def __hash__(self) -> int:
        return hash((
            tuple(self.hallway),
            tuple(tuple(room) for room in self.rooms)
        ))

    def _hallway_str(self) -> str:
        return str(self.hallway[0]) \
            + str(self.hallway[1])  \
            + "."                  \
            + str(self.hallway[2])  \
            + "."                  \
            + str(self.hallway[3])  \
            + "."                  \
            + str(self.hallway[4])  \
            + "."                  \
            + str(self.hallway[5])  \
            + str(self.hallway[6])

    def __str__(self) -> str:
        return "#############\n" \
            f"#{self._hallway_str()}#\n" \
            f"###{self.rooms[0][1]}#{self.rooms[1][1]}#{self.rooms[2][1]}#{self.rooms[3][1]}###\n"\
            f"  #{self.rooms[0][0]}#{self.rooms[1][0]}#{self.rooms[2][0]}#{self.rooms[3][0]}#  \n"\
            "  #########  \n"

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

    @staticmethod
    def unwrap_hallway_index(i: int) -> int:
        if i <= 1:
            return i
        elif i <= 5:
            return 2*i - 1
        else:
            return i + 4

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
                    distance_to_room = abs(self.unwrap_hallway_index(idx) - 2 * (amphipod + 1))
                    energy_delta = amphipod.energy_multiplier() * (2 + distance_to_room)
                    yield State(
                        self.burrow.to_room(idx, amphipod, 0),
                        self.energy + energy_delta
                    )

                # Move into a room where the "window" seat is occupied by the expected amphipod
                elif self.burrow.rooms[amphipod][0] == amphipod and \
                        self.burrow.rooms[amphipod][1] == Spot.Empty:
                    distance_to_room = abs(self.unwrap_hallway_index(idx) - 2 * (amphipod + 1))
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

                energy_delta = abs(self.unwrap_hallway_index(hallway_idx) - 2 * (room_idx + 1))
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
    hallway: list[Spot] = [Spot.Empty] * HALLWAY_LENGTH

    # Test input
    # rooms: list[list[Spot]] = [
    #     [Spot.A, Spot.B],
    #     [Spot.D, Spot.C],
    #     [Spot.C, Spot.B],
    #     [Spot.A, Spot.D],
    # ]

    # Normal input
    rooms: list[list[Spot]] = [
        [Spot.C, Spot.D],
        [Spot.A, Spot.A],
        [Spot.B, Spot.C],
        [Spot.B, Spot.D],
    ]

    state = State(Burrow(hallway, rooms))
    state = find_cheapest(state)
    print(state.energy)
