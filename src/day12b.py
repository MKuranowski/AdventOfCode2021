from fileinput import FileInput
from typing import Optional
from day12a import Graph, Path, make_graph


def find_all_paths(graph: Graph) -> set[Path]:
    finished: set[Path] = set()

    # The second element represents which small cave was visited twice
    queue: set[tuple[Path, Optional[str]]] = {(("start", ), None)}

    while queue:
        path_so_far, small_cave_visited_twice = queue.pop()
        _, adjacent = graph[path_so_far[-1]]

        for node in adjacent:
            with_node_appended = tuple(list(path_so_far) + [node])

            if node == "end":
                finished.add(with_node_appended)

            elif node == "start":
                continue  # Cannot visit start more than once

            elif node.isupper() or node not in path_so_far:
                # Big cave or a non-visited small cave
                queue.add((with_node_appended, small_cave_visited_twice))

            elif small_cave_visited_twice is None:
                # Small cave, that we already visited;
                # however none other small cave was already visited twice.
                queue.add((with_node_appended, node))

    return finished


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    graph = make_graph(input)
    paths = find_all_paths(graph)
    print(len(paths))
