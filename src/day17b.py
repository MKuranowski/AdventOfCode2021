from day17a import TARGET_RIGHT, ShotResult, shoot


def brute_force_all() -> int:
    count = 0

    for vel_x in range(1, TARGET_RIGHT+1):
        for vel_y in range(-100, 500):
            result, _ = shoot(vel_x, vel_y)

            if result == ShotResult.WITHIN:
                count += 1

            elif result == ShotResult.OVERSHOT:
                break

    return count


if __name__ == "__main__":
    print(brute_force_all())
