# https://en.wikipedia.org/wiki/Variable-length_quantity
def variable_length_encode(i):
    encoded = []

    bit_length = len(bin(i)[2:])
    encoded.append(i & 127)

    while bit_length > 7:
        i >>= 7
        bit_length -= 7
        encoded.insert(0, (i & 127) + 128)

    return bytes(encoded)
