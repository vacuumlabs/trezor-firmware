from apps.cardano.helpers.paths import ACCOUNT_PATH_INDEX, unharden

if False:
    from typing import List


def variable_length_encode(number: int) -> bytes:
    """
    Used for pointer encoding in pointer address.
    Encoding description can be found here:
    https://en.wikipedia.org/wiki/Variable-length_quantity
    """
    if number < 0:
        raise ValueError("Negative numbers not supported. Number supplied: %s" % number)

    encoded = []

    bit_length = len(bin(number)[2:])
    encoded.append(number & 127)

    while bit_length > 7:
        number >>= 7
        bit_length -= 7
        encoded.insert(0, (number & 127) + 128)

    return bytes(encoded)


def to_account_path(path: List[int]) -> List[int]:
    return path[: ACCOUNT_PATH_INDEX + 1]


def format_account_number(path: List[int]) -> string:
    if len(path) <= ACCOUNT_PATH_INDEX:
        raise ValueError("Path is too short.")

    return "#%d" % (unharden(path[ACCOUNT_PATH_INDEX]) + 1)
