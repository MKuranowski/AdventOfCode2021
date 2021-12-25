from fileinput import FileInput
from typing import Iterable, NamedTuple

# There's no corresponding input/16-test, as there are multiple different examples provided.
# Testing is done via `echo HEX_PACKET | python src/day16a.py`.


class LiteralPacket(NamedTuple):
    version: int
    type_id: int
    value: int

    def recursive_version_sum(self) -> int:
        return self.version

    def eval(self) -> int:
        return self.value


class OperatorPacket(NamedTuple):
    version: int
    type_id: int
    sub_packets: list["Packet"]

    def recursive_version_sum(self) -> int:
        return self.version + sum(i.recursive_version_sum() for i in self.sub_packets)

    def eval(self) -> int:
        match self.type_id:
            case 0:
                return sum(i.eval() for i in self.sub_packets)
            case 1:
                return product(i.eval() for i in self.sub_packets)
            case 2:
                return min(i.eval() for i in self.sub_packets)
            case 3:
                return max(i.eval() for i in self.sub_packets)
            case 5:
                assert len(self.sub_packets) == 2
                return int(self.sub_packets[0].eval() > self.sub_packets[1].eval())
            case 6:
                assert len(self.sub_packets) == 2
                return int(self.sub_packets[0].eval() < self.sub_packets[1].eval())
            case 7:
                assert len(self.sub_packets) == 2
                return int(self.sub_packets[0].eval() == self.sub_packets[1].eval())
            case _:
                raise ValueError(f"Unknown operator type: {self.type_id}")


Packet = LiteralPacket | OperatorPacket

DIGIT_TO_BIN = {
    "0": "0000", "1": "0001", "2": "0010", "3": "0011", "4": "0100", "5": "0101", "6": "0110",
    "7": "0111", "8": "1000", "9": "1001", "A": "1010", "B": "1011", "C": "1100", "D": "1101",
    "E": "1110", "F": "1111"
}


def product(xs: Iterable[int]) -> int:
    result = 1
    for x in xs:
        result *= x
    return result


def to_binary_string(hex: str) -> str:
    return "".join(DIGIT_TO_BIN[digit.upper()] for digit in hex)


def eat_padding(stream: str, no_padding: bool = False) -> str:
    if no_padding:
        return stream

    # Ensure nibble alignment
    stream = stream[len(stream) % 4:]

    # Eat zero nibbles
    while stream[:4] == "0000":
        stream = stream[4:]

    return stream


def consume_packet(stream: str, no_padding: bool = False) -> tuple[Packet, str]:
    # Consume the version
    version = int(stream[:3], 2)
    type_id = int(stream[3:6], 2)
    stream = stream[6:]

    if type_id == 4:
        # Literal Packet
        # Consume the value
        more = True
        value = 0

        while more:
            more = stream[0] == "1"
            nibble = int(stream[1:5], 2)
            value = (value << 4) | nibble
            stream = stream[5:]

        # Consume the padding
        return LiteralPacket(version, type_id, value), eat_padding(stream, no_padding)

    # Operator packet
    length_type_id, stream = stream[0], stream[1:]
    sub_packets: list[Packet] = []

    if length_type_id == "0":
        # Actual length
        total_length = int(stream[:15], 2)
        consumed = 0

        stream = stream[15:]

        while consumed < total_length:
            stream_len_before = len(stream)
            packet, stream = consume_packet(stream, no_padding=True)
            sub_packets.append(packet)
            consumed += stream_len_before - len(stream)

        assert consumed == total_length

    else:
        to_consume = int(stream[:11], 2)
        stream = stream[11:]

        for _ in range(to_consume):
            packet, stream = consume_packet(stream, no_padding=True)
            sub_packets.append(packet)

    return OperatorPacket(version, type_id, sub_packets), eat_padding(stream, no_padding)


if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    line = next(input).strip()
    stream = to_binary_string(line)

    packet, stream = consume_packet(stream)
    print(packet.recursive_version_sum())
