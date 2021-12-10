from fileinput import FileInput
from typing import Optional

EXPECTED_OPEN_BRACKET: dict[str, str] = {
    ")": "(",
    "]": "[",
    "}": "{",
    ">": "<",
}

SCORES: dict[str, int] = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}


def incorrect_brackets(line: str) -> Optional[str]:
    stack: list[str] = []

    for char in line:
        # Open brackets
        if char in {"(", "[", "{", "<"}:
            stack.append(char)

        # Consume brackets
        elif char in EXPECTED_OPEN_BRACKET:
            if stack[-1] == EXPECTED_OPEN_BRACKET[char]:
                stack.pop()
            else:
                return char

        else:
            assert False, f"invalid char: {char!r}"


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    total: int = 0

    for line in (i.strip() for i in input):
        incorrect_bracket = incorrect_brackets(line)
        if incorrect_bracket:
            total += SCORES[incorrect_bracket]

    print(total)
