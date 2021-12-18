from dataclasses import dataclass
from typing import Optional, Union
from fileinput import FileInput
import re

SN = Union["SNLeaf", "SNNode"]


@dataclass
class SNLeaf:
    value: int
    parent: Optional["SNNode"] = None

    def __str__(self) -> str:
        return str(self.value)

    def copy(self, new_parent: Optional["SNNode"] = None) -> "SNLeaf":
        return SNLeaf(self.value, new_parent)

    def magnitude(self) -> int:
        return self.value

    def add_to_leftmost(self, i: int) -> None:
        self.value += i

    def add_to_rightmost(self, i: int) -> None:
        self.value += i

    def split(self) -> bool:
        if self.value < 10:
            return False

        x, y = divmod(self.value, 2)
        new_left_node = SNLeaf(x)
        new_right_node = SNLeaf(x + y)
        new_node = SNNode(new_left_node, new_right_node, self.parent)
        new_left_node.parent = new_node
        new_right_node.parent = new_node

        assert self.parent

        if self.parent.left is self:
            self.parent.left = new_node
        else:
            self.parent.right = new_node

        return True

    def reduce(self) -> None:
        pass  # Reducing a leaf does nothing


@dataclass
class SNNode:
    left: SN
    right: SN
    parent: Optional["SNNode"] = None

    def __str__(self) -> str:
        return f"[{self.left!s},{self.right!s}]"

    @staticmethod
    def from_str(t: str) -> tuple[SN, str]:
        if t[0] != "[":
            num, rest = re.split(r"(?=\D)", t, maxsplit=1)
            return SNLeaf(int(num)), rest

        else:
            left, t = SNNode.from_str(t[1:])
            assert t[0] == ","
            right, t = SNNode.from_str(t[1:])
            assert t[0] == "]"
            nd = SNNode(left, right)
            left.parent = nd
            right.parent = nd
            return nd, t[1:]

    def copy(self, new_parent: Optional["SNNode"] = None) -> "SNNode":
        new_node = SNNode(self.left, self.right, new_parent)
        new_node.left = self.left.copy(new_node)
        new_node.right = self.right.copy(new_node)
        return new_node

    def magnitude(self) -> int:
        return 3*self.left.magnitude() + 2*self.right.magnitude()

    def add(self, other: SN) -> "SNNode":
        assert self.parent is None, "added can only be done at the top level"
        new_node = SNNode(self, other)
        new_node.left = self.copy(new_node)
        new_node.right = other.copy(new_node)
        new_node.reduce()
        return new_node

    def add_to_leftmost(self, i: int) -> None:
        self.left.add_to_leftmost(i)

    def add_to_leftmost_in_other_subtree(self, i: int) -> None:
        node: SNNode = self

        while True:
            if node.parent is None:
                return
            elif node.parent.right is node:
                node = node.parent
            else:
                # Finally, a different subtree
                node.parent.right.add_to_leftmost(i)
                return

    def add_to_rightmost(self, i: int) -> None:
        self.right.add_to_rightmost(i)

    def add_to_rightmost_in_other_subtree(self, i: int) -> None:
        node: SNNode = self

        while True:
            if node.parent is None:
                return
            elif node.parent.left is node:
                node = node.parent
            else:
                # Finally, a different subtree
                node.parent.left.add_to_rightmost(i)
                return

    def do_explode(self) -> bool:
        # Self needs to be gone
        assert isinstance(self.parent, SNNode)
        assert isinstance(self.left, SNLeaf)
        assert isinstance(self.right, SNLeaf)

        # Left replacement
        if self.parent.left is self:
            self.parent.left = SNLeaf(0, self.parent)
            self.parent.right.add_to_leftmost(self.right.value)
            self.parent.add_to_rightmost_in_other_subtree(self.left.value)

        else:
            self.parent.right = SNLeaf(0, self.parent)
            self.parent.left.add_to_rightmost(self.left.value)
            self.parent.add_to_leftmost_in_other_subtree(self.right.value)

        return True

    def explode(self, depth: int = 0) -> bool:
        # Base case for the recursion
        if depth == 4:
            return self.do_explode()

        # Recursive case
        did_explode: bool = False

        # Try to explode in DFS order
        if isinstance(self.left, SNNode):
            did_explode = self.left.explode(depth + 1)

        if isinstance(self.right, SNNode) and not did_explode:
            did_explode = self.right.explode(depth + 1)

        return did_explode

    def split(self) -> bool:
        # DFS to find a node to split
        return self.left.split() or self.right.split()

    def reduce(self) -> None:
        did_something: bool = True
        while did_something:
            did_something = self.explode() or self.split()


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    result: Optional[SNNode] = None

    for line in input:
        nd, _ = SNNode.from_str(line.strip())
        if result is None:
            assert isinstance(nd, SNNode)
            result = nd
        else:
            result = result.add(nd)

    assert result
    print(result.magnitude())
