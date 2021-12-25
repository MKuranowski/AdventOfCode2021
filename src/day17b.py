from fileinput import FileInput

from day17a import BLTR, ShotResult, shoot


def brute_force_all(target: BLTR) -> int:
    count = 0

    for vel_x in range(1, target.right+1):
        for vel_y in range(-100, 500):
            result, _ = shoot(vel_x, vel_y, target)

            if result == ShotResult.WITHIN:
                count += 1

            elif result == ShotResult.OVERSHOT:
                break

    return count


if __name__ == "__main__":
    target = BLTR.from_input(next(FileInput()).strip())
    print(brute_force_all(target))
