from fileinput import FileInput
from itertools import permutations

from day18a import SNNode


def sn_node_from_str(t: str) -> SNNode:
    nd, _ = SNNode.from_str(t)
    assert isinstance(nd, SNNode)
    return nd


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    all_numbers: list[SNNode] = [sn_node_from_str(i.strip()) for i in input]
    max_magnitude: int = -1

    for left, right in permutations(all_numbers, 2):
        result = left.add(right)
        res_magnitude = result.magnitude()
        if res_magnitude > max_magnitude:
            max_magnitude = res_magnitude

    print(max_magnitude)
