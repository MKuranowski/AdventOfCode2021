from typing import Callable, Iterable, TypeVar


_T = TypeVar("_T")


def empty_str(t: str) -> bool:
    return t == ""


def split_on(seq: Iterable[_T], pred: Callable[[_T], bool]) -> list[list[_T]]:
    after_split: list[list[_T]] = []
    current: list[_T] = []

    for elem in seq:
        if pred(elem):
            # Split on this element
            if current:
                after_split.append(current)
            current = []
        else:
            current.append(elem)

    if current:
        after_split.append(current)

    return after_split
