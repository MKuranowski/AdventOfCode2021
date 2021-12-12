from fileinput import FileInput
from typing import Iterable


Node = tuple[str, set[str]]
Graph = dict[str, Node]

Path = tuple[str, ...]


def make_graph(lines: Iterable[str]) -> Graph:
    graph: Graph = {}

    for line in lines:
        left, _, right = line.strip().partition("-")

        graph.setdefault(left, (left, set()))
        graph.setdefault(right, (right, set()))

        graph[left][1].add(right)
        graph[right][1].add(left)

    return graph


def find_all_paths(graph: Graph) -> set[Path]:
    finished: set[Path] = set()
    queue: set[Path] = {("start", )}

    while queue:
        to_expand = queue.pop()
        _, adjacent = graph[to_expand[-1]]

        for node in adjacent:
            if node == "end":
                finished.add(tuple(list(to_expand) + [node]))
            elif node.isupper() or (node not in to_expand):
                queue.add(tuple(list(to_expand) + [node]))

    return finished


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    graph = make_graph(input)
    paths = find_all_paths(graph)
    print(len(paths))
