from typing import Callable, Iterable, TypeVar

_T = TypeVar("_T")
_K = TypeVar("_K")


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


def aggregate_by(iterable: Iterable[_T], key: Callable[[_T], _K]) -> dict[_K, list[_T]]:
    """Groups elements from an iterable by key(elem).
    Analogous to itertools.group_by; however this function doesn't care about the order
    of the keys.
    """
    d: dict[_K, list[_T]] = {}
    for elem in iterable:
        d.setdefault(key(elem), []).append(elem)
    return d
