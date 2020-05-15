from trezor import log
from trezor.crypto import base58, crc, hashlib

from apps.common import cbor
from apps.common.seed import remove_ed25519_prefix


def _encode_address_raw(address_data_encoded):
    return base58.encode(
        cbor.encode(
            [cbor.Tagged(24, address_data_encoded), crc.crc32(address_data_encoded)]
        )
    )


def derive_address_and_node(keychain, path: list):
    node = keychain.derive(path)

    address_payload = None
    address_attributes = {}

    address_root = _get_address_root(node, address_payload)
    address_type = 0
    address_data = [address_root, address_attributes, address_type]
    address_data_encoded = cbor.encode(address_data)

    return _encode_address_raw(address_data_encoded)


def is_safe_output_address(address) -> bool:
    """
    Determines whether it is safe to include the address as-is as
    a tx output, preventing unintended side effects (e.g. CBOR injection)
    """
    try:
        address_hex = base58.decode(address)
        address_unpacked = cbor.decode(address_hex)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        return False

    if not isinstance(address_unpacked, list) or len(address_unpacked) != 2:
        return False

    address_data_encoded = address_unpacked[0]

    if not isinstance(address_data_encoded, bytes):
        return False

    return _encode_address_raw(address_data_encoded) == address


def _address_hash(data) -> bytes:
    data = cbor.encode(data)
    data = hashlib.sha3_256(data).digest()
    res = hashlib.blake2b(data=data, outlen=28).digest()
    return res


def _get_address_root(node, payload):
    extpubkey = remove_ed25519_prefix(node.public_key()) + node.chain_code()
    if payload:
        payload = {1: cbor.encode(payload)}
    else:
        payload = {}
    return _address_hash([0, [0, extpubkey], payload])
