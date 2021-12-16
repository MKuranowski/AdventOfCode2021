from fileinput import FileInput

from day16a import to_binary_string, consume_packet

# There's no corresponding input/16-test, as there are multiuple different examples provided.
# Testing is done via `echo HEX_PACKET | python src/day16b.py`.

# The implementation is actually included in the day16a.py file
# It's much easier to implement the evaluation as methods on Packets.

if __name__ == "__main__":
    input: "FileInput[str]" = FileInput()
    line = next(input).strip()
    stream = to_binary_string(line)

    packet, stream = consume_packet(stream)
    print(packet.eval())
