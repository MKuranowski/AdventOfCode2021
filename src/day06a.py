from collections import Counter
from fileinput import FileInput


def simulate(state: Counter[int], cycles: int) -> int:
    new_state: Counter[int]

    for day in range(cycles):
        new_state = Counter()

        for counter_value, count in state.items():
            if counter_value == 0:
                new_state[6] += count
                new_state[8] += count
            else:
                new_state[counter_value - 1] += count

        state = new_state

    return sum(state.values())


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    initial_population = map(int, next(input).rstrip().split(","))
    initial_state = Counter(initial_population)
    result = simulate(initial_state, 80)
    print(result)
