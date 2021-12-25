from fileinput import FileInput

import day23a


if __name__ == "__main__":
    day23a.ROOM_SIZE = 4

    initial_burrow = day23a.Burrow.from_input(FileInput())
    initial_state = day23a.State(initial_burrow)

    cheapest_end_state = day23a.find_cheapest(initial_state)
    print(cheapest_end_state.energy)
