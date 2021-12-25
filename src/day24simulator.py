from dataclasses import dataclass, field
from typing import Callable, ClassVar, Iterable, MutableSequence, NewType
from fileinput import FileInput
import operator

from core import split_on


REGISTER_STRINGS = frozenset(("w", "x", "y", "z"))
Register = NewType("Register", int)


@dataclass
class ALU:
    # registers[0] → w, [1] → x, [2] → y, [3] → z
    registers: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    input_queue: MutableSequence[int] = field(default_factory=list)

    OPS: ClassVar[dict[str, Callable[[int, int], int]]] = {
        "add": operator.add,
        "mul": operator.mul,
        "div": operator.floordiv,
        "mod": operator.mod,
        "eql": lambda a, b: int(operator.eq(a, b)),
    }

    @staticmethod
    def as_register(operand: str) -> Register:
        return Register(ord(operand) - ord("w"))

    @staticmethod
    def as_int(operand: str) -> int:
        if not operand:
            return 0
        return int(operand)

    def inp(self, dest: Register) -> None:
        self.registers[dest] = self.input_queue.pop()

    def exec_line(self, line: str) -> None:
        op, _, args = line.partition(" ")
        dest_str, _, src_str = args.partition(" ")

        assert dest_str in REGISTER_STRINGS
        dest = self.as_register(dest_str)

        # Special case for the input operation
        if op == "inp":
            return self.inp(dest)

        src = self.registers[self.as_register(src_str)] if src_str in REGISTER_STRINGS \
            else self.as_int(src_str)

        op_func = self.OPS[op]
        self.registers[dest] = op_func(self.registers[dest], src)

    def exec_prog(self, prog: Iterable[str]) -> None:
        for line in prog:
            self.exec_line(line)


if __name__ == "__main__":
    alu = ALU()
    prog: list[str] = [i.strip() for i in FileInput()]
    prog_per_digit = split_on(prog, lambda i: i == "inp w")

    digits = [9, 6, 9, 1, 8, 9, 9, 6, 9, 2, 4, 9, 9, 1]

    for i, digit in enumerate(digits):
        alu.registers[0] = digit
        alu.exec_prog(prog_per_digit[i])

        print("Registers after step no", i, "-", alu.registers)
