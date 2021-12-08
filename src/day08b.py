import operator
from fileinput import FileInput
from functools import reduce
from typing import Iterable

from core import aggregate_by

Guess = dict[str, set[str]]
Bins = tuple[Guess, Guess, Guess]


DIGITS: dict[frozenset[str], str] = {
    # cSpell: disable
    frozenset("abcefg"): "0",
    frozenset("cf"): "1",
    frozenset("acdeg"): "2",
    frozenset("acdfg"): "3",
    frozenset("bcdf"): "4",
    frozenset("abdfg"): "5",
    frozenset("abdefg"): "6",
    frozenset("acf"): "7",
    frozenset("abcdefg"): "8",
    frozenset("abcdfg"): "9",
    # cSpell: enable
}


def info_from_unique(input: set[str]) -> Guess:
    """Infer information from a randomized input.
    Returns a mapping from an output to all possible inputs
    """
    if len(input) == 2:
        # Digit 1
        return {
            "c": input,
            "f": input,
        }

    elif len(input) == 3:
        # Digit 7
        return {
            "a": input,
            "c": input,
            "f": input,
        }

    elif len(input) == 4:
        return {
            "b": input,
            "c": input,
            "d": input,
            "f": input,
        }

    else:
        raise ValueError(f"{len(input)}-segment inputs are not unique (or useful, lol)")

    # Any other length are not helpful:
    # len 5 - digits 2, 3, 5 - not unique
    # len 6 - digits 0, 6, 9 - not unique
    # len 7 - digit 8 - pointless, doesn't convey any info


def info_from_five_segments(five_segment_inputs: Iterable[set[str]]) -> Guess:
    """Infers possible mappings from all of the inputs of length 5"""
    # digits 2, 3, 5
    intersection: set[str] = reduce(operator.and_, five_segment_inputs)
    assert len(intersection) == 3

    return {
        "a": intersection,
        "d": intersection,
        "g": intersection,
    }


def info_from_six_segments(six_segment_inputs: Iterable[set[str]]) -> Guess:
    """Infers possible mappings from all of the inputs of length 5"""
    # digits 0, 6, 9
    intersection: set[str] = reduce(operator.and_, six_segment_inputs)
    assert len(intersection) == 4

    return {
        "a": intersection,
        "b": intersection,
        "f": intersection,
        "g": intersection,
    }


def update_guess(guess: Guess, info: Guess) -> None:
    for segment, possibilities in info.items():
        guess[segment].intersection_update(possibilities)


def _into_bins(guess: Guess) -> Bins:
    bin0: Guess = {}
    bin1: Guess = {}
    bin2: Guess = {}

    for segment, possibilities in guess.items():
        if len(possibilities) == 0:
            bin0[segment] = possibilities
        elif len(possibilities) == 1:
            bin1[segment] = possibilities
        else:
            bin2[segment] = possibilities

    return bin0, bin1, bin2


def simplify_solution(guess: Guess) -> dict[str, str]:
    solution: dict[str, str] = {}
    all_known_mapped_to: set[str] = set()

    while guess:
        bin0, bin1, bin2 = _into_bins(guess)

        if bin0:
            # Some segments end up without a possible mapping
            raise ValueError("no solution")

        elif bin1:
            # Extract data
            for segment, mapped_to_set in bin1.items():
                mapped_to = mapped_to_set.pop()
                assert not mapped_to_set
                assert mapped_to not in all_known_mapped_to

                all_known_mapped_to.add(mapped_to)
                solution[segment] = mapped_to

            # Update the last bin
            for possibilities in bin2.values():
                possibilities.difference_update(all_known_mapped_to)

            guess = bin2

        elif bin2:
            # Some segments end up without multiple possibilities,
            # bo no more intersections can't be calculated
            raise ValueError("no solution")

    return solution


def find_mapping(inputs: Iterable[str]) -> dict[str, str]:
    # Start by assuming that every input could map to every output
    guess: dict[str, set[str]] = {segment: set("abcdefg") for segment in "abcdefg"}
    inputs_by_length: dict[int, list[set[str]]] = aggregate_by(map(set, inputs), len)

    # Assert correct groupings
    assert len(inputs_by_length[2]) == 1
    assert len(inputs_by_length[3]) == 1
    assert len(inputs_by_length[4]) == 1
    assert len(inputs_by_length[5]) == 3
    assert len(inputs_by_length[6]) == 3
    assert len(inputs_by_length[7]) == 1

    # Infer info from unique-length digits
    update_guess(guess, info_from_unique(inputs_by_length[2][0]))
    update_guess(guess, info_from_unique(inputs_by_length[3][0]))
    update_guess(guess, info_from_unique(inputs_by_length[4][0]))

    # Infer info from five- and six-segment digits
    update_guess(guess, info_from_five_segments(inputs_by_length[5]))
    update_guess(guess, info_from_six_segments(inputs_by_length[6]))

    return simplify_solution(guess)


def decode_digit(output: str, mapping: dict[str, str]) -> str:
    mapped_output = frozenset(mapping[segment] for segment in output)
    return DIGITS[mapped_output]


def decode_number(outputs: Iterable[str], mapping: dict[str, str]) -> int:
    number = "".join(decode_digit(output, mapping) for output in outputs)
    return int(number)


def decode_line(line: str) -> int:
    inputs, _, outputs = line.partition(" | ")
    mapping = find_mapping(inputs.split())
    reversed_mapping = {v: k for k, v in mapping.items()}
    return decode_number(outputs.split(), reversed_mapping)


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    print(sum(decode_line(line.strip()) for line in input))
