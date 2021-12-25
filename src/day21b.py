from fileinput import FileInput
from functools import lru_cache

from day21a import parse_player_positions

BOARD_SIZE = 10
WON_TRESHOLD = 21

# List of (advance, count)
ROLL_OUTPUTS: list[tuple[int, int]] = [
    (3+0, 1),
    (3+1, 3),
    (3+2, 6),
    (3+3, 7),
    (3+4, 6),
    (3+5, 3),
    (3+6, 1),
]

Player = tuple[int, int]  # pos, score


def player_moved(p: Player, advance: int) -> Player:
    new_pos = (p[0] + advance) % BOARD_SIZE
    return new_pos, p[1] + new_pos + 1


@lru_cache(maxsize=128 * 1024)
def DFS(turn: int, p1: Player, p2: Player) -> tuple[int, int]:
    current_p = p1 if turn == 0 else p2
    previous_p = p2 if turn == 0 else p1

    # Base case - if the previous player has won
    if previous_p[1] >= WON_TRESHOLD:
        return (0, 1) if turn == 0 else (1, 0)

    # Recursive case
    p1_won_total = 0
    p2_won_total = 0

    for advance, multiplier in ROLL_OUTPUTS:
        current_moved = player_moved(current_p, advance)
        p1_won, p2_won = DFS(
            turn ^ 1,
            current_moved if turn == 0 else previous_p,
            previous_p if turn == 0 else current_moved,
        )
        p1_won_total += p1_won * multiplier
        p2_won_total += p2_won * multiplier

    return p1_won_total, p2_won_total


if __name__ == "__main__":
    p1_start_pos, p2_start_pos = parse_player_positions(FileInput())

    p1: Player = p1_start_pos - 1, 0
    p2: Player = p2_start_pos - 1, 0

    p1_won, p2_won = DFS(0, p1, p2)
    print(max(p1_won, p2_won))
