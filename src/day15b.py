from fileinput import FileInput
from day15a import Map, a_star

Tiles = list[list[Map]]


def copy_tile_add_one(tile: Map) -> Map:
    return [[(cell % 9) + 1 for cell in row] for row in tile]


def make_bigger_map(first_tile: Map) -> Tiles:
    tiles: Tiles = [[first_tile]]

    # First, make new rows
    for _ in range(4):
        tiles.append([copy_tile_add_one(tiles[-1][0])])

    # First, make new columns
    for row in tiles:
        for _ in range(4):
            row.append(copy_tile_add_one(row[-1]))

    return tiles


def merge_tiles(tiles: Tiles, tile_size: int) -> Map:
    map: Map = []

    for row_of_tiles in tiles:
        for inner_idx in range(tile_size):
            row: list[int] = []
            for tile in row_of_tiles:
                row.extend(tile[inner_idx])
            map.append(row)

    return map


def dump_map(map: Map) -> None:
    for row in map:
        print("".join(str(value) for value in row))


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()

    tile: Map = [[int(cell) for cell in line.strip()] for line in input]
    tile_size = len(tile)  # maps are square

    map = merge_tiles(make_bigger_map(tile), tile_size)
    size = tile_size * 5

    path = a_star((0, 0), (size-1, size-1), map, size)
    result = sum(map[x][y] for x, y in path) - map[0][0]
    print(result)
