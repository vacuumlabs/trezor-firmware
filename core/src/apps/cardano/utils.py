from trezor.crypto import hashlib

from apps.common.seed import remove_ed25519_prefix


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


def get_public_key_hash(keychain, path) -> bytes:
    node = keychain.derive(path)
    public_key = remove_ed25519_prefix(node.public_key())
    return hashlib.blake2b(data=public_key, outlen=28).digest()
