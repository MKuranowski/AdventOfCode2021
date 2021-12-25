from typing import NamedTuple

# This is the simplified progra; it can only perform the following operations.
#
# If the digit-processing part has a `div z 1`, the whole digit processing is an OP1.
# The parameter is the number at the last `y`.
# Because the STH in the initial `add x STH` is always >= 10, the `equ x w`
# will always fail (as w is a digit, aka. < 10).
#
# Otherwise, there's a `div z 26`. In this case, the operation is a OP2,
# where the comparison with x can go both ways.
# x_param is the absolute value in the initial `add x ...`.
# In the program this number is always negative.
# y_param is the argument of the final `add y ...`.


class OP1(NamedTuple):
    param_y: int

    def perform(self, z: int, digit: int) -> int:
        return (26 * z) + digit + self.param_y


class OP2(NamedTuple):
    param_x: int
    param_y: int

    def perform(self, z: int, digit: int) -> int:
        z, mod = divmod(z, 26)
        x = mod - self.param_x
        return z if x == digit else OP1(self.param_y).perform(z, digit)


OPS: list[OP1 | OP2] = [
    OP1(5),
    OP1(5),
    OP1(1),
    OP1(15),
    OP1(2),
    OP2(1, 2),
    OP1(5),
    OP2(8, 8),
    OP2(7, 14),
    OP2(8, 12),
    OP1(7),
    OP2(2, 14),
    OP2(2, 13),
    OP2(13, 6),
]


def optimized_monad(digits: list[int]) -> int:
    assert len(digits) == len(OPS)
    z: int = 0

    for op, digit in zip(OPS, digits):
        z = op.perform(z, digit)

    return z

# === REVERSING === #
# We can see that most operations on z multiply the number by 26 or divide it by 26.
# If there was a symmetric number of operations, then we should arrive at the starting z = 0.
# This means that we want to __always__ hit the `x == digit` branch in op2.
#
# The whole program can also be interpreted as a stack of numbers from <0, 25>,
# where push is done as `stack = (stack * 26) + number`
# and a pop is done as `stack, number = divmod(stack, 26)`.
#
# The issue is with handling the offsets.
# OP1 pushes `(digit + param_y)`.
# OP2 pops if and only if `(popped - param_x == digit)`


def potential_digits(big_first: bool = True) -> list[int]:
    if big_first:
        return [9, 8, 7, 6, 5, 4, 3, 2, 1]
    else:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9]


class OPPair(NamedTuple):
    push_digit_idx: int
    pop_digit_idx: int
    push_offset: int
    pop_offset: int

    def solve_into(self, digits: list[int], big_first: bool) -> None:
        for potential_push in potential_digits(big_first):
            potential_pop = potential_push + self.push_offset - self.pop_offset
            if 1 <= potential_pop <= 9:
                digits[self.push_digit_idx] = potential_push
                digits[self.pop_digit_idx] = potential_pop
                return


def op_pairs() -> list[OPPair]:
    op1_idx_stack: list[int] = []
    pairs: list[OPPair] = []

    for idx, op in enumerate(OPS):
        match op:
            case OP1():
                op1_idx_stack.append(idx)
            case OP2():
                op1_idx = op1_idx_stack.pop()
                pairs.append(OPPair(
                    op1_idx,
                    idx,
                    OPS[op1_idx].param_y,
                    op.param_x,
                ))

    return pairs


if __name__ == "__main__":
    digits = [-1] * 14

    for solve_pair in op_pairs():
        solve_pair.solve_into(digits, True)

    print("".join(map(str, digits)))
