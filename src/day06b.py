from fileinput import FileInput
from collections import Counter

from day06a import simulate

if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    initial_population = map(int, next(input).rstrip().split(","))
    initial_state = Counter(initial_population)
    result = simulate(initial_state, 256)
    print(result)
