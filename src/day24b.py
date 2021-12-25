from day24a import op_pairs

if __name__ == "__main__":
    digits = [-1] * 14

    for solve_pair in op_pairs():
        solve_pair.solve_into(digits, False)

    print("".join(map(str, digits)))
