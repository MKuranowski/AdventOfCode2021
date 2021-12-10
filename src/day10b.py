from fileinput import FileInput
from statistics import median
from typing import Iterable

EXPECTED_OPEN_BRACKET: dict[str, str] = {
    ")": "(",
    "]": "[",
    "}": "{",
    ">": "<",
}

SCORES: dict[str, int] = {
    "(": 1,
    "[": 2,
    "{": 3,
    "<": 4,
}


def autocomplete_score(line: str) -> int:
    stack: list[str] = []

    # Consume the stack, discarding input on mismatch
    for char in line:
        # Open brackets
        if char in {"(", "[", "{", "<"}:
            stack.append(char)

        # Consume brackets
        elif char in EXPECTED_OPEN_BRACKET:
            if stack[-1] == EXPECTED_OPEN_BRACKET[char]:
                stack.pop()
            else:
                return 0

        else:
            assert False, f"invalid char: {char!r}"

    # Generate auto-completion score
    score: int = 0
    for char in reversed(stack):
        score *= 5
        score += SCORES[char]
    return score


def autocomplete_scores(input: Iterable[str]) -> Iterable[int]:
    for line in input:
        score = autocomplete_score(line.strip())
        if score:
            yield score


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    print(median(autocomplete_scores(input)))
