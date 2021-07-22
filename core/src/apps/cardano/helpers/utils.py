from trezor.crypto import hashlib
from trezor.enums import CardanoTxSigningMode

from apps.cardano.helpers.paths import (
    ACCOUNT_PATH_INDEX,
    SCHEMA_STAKING_ANY_ACCOUNT,
    unharden,
)
from apps.common.seed import remove_ed25519_prefix

from ...common.layout import address_n_to_str
from . import ADDRESS_KEY_HASH_SIZE, SCRIPT_HASH_SIZE, bech32
from .bech32 import HRP_SCRIPT_HASH

if False:
    from trezor import wire
    from trezor.messages import CardanoBlockchainPointerType
    from trezor.ui.layouts import PropertyType
    from .. import seed


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


def to_account_path(path: list[int]) -> list[int]:
    return path[: ACCOUNT_PATH_INDEX + 1]


def format_account_number(path: list[int]) -> str:
    if len(path) <= ACCOUNT_PATH_INDEX:
        raise ValueError("Path is too short.")

    return "#%d" % (unharden(path[ACCOUNT_PATH_INDEX]) + 1)


def format_optional_int(number: int | None) -> str:
    if number is None:
        return "n/a"

    return str(number)


def format_stake_pool_id(pool_id_bytes: bytes) -> str:
    return bech32.encode("pool", pool_id_bytes)


def format_asset_fingerprint(policy_id: bytes, asset_name_bytes: bytes) -> str:
    fingerprint = hashlib.blake2b(
        # bytearrays are being promoted to bytes: https://github.com/python/mypy/issues/654
        # but bytearrays are not concatenable, this casting works around this limitation
        data=bytes(policy_id) + bytes(asset_name_bytes),
        outlen=20,
    ).digest()

    return bech32.encode("asset", fingerprint)


def format_script_hash(script_hash: bytes) -> str:
    return bech32.encode(HRP_SCRIPT_HASH, script_hash)


def get_set_credential(
    path: list[int],
    key_hash: bytes | None,
    script_hash: bytes | None,
    pointer: CardanoBlockchainPointerType | None,
) -> list[int] | bytes | CardanoBlockchainPointerType | None:
    if path:
        return path
    elif key_hash:
        return key_hash
    elif script_hash:
        return script_hash
    elif pointer:
        return pointer
    else:
        return None


def get_set_credential_title(
    path: list[int],
    key_hash: bytes | None,
    script_hash: bytes | None,
    pointer: CardanoBlockchainPointerType | None,
) -> str:
    if path:
        return "path"
    elif key_hash:
        return "key hash"
    elif script_hash:
        return "script"
    elif pointer:
        return "pointer"
    else:
        return ""


def format_credential(
    path: list[int],
    key_hash: bytes | None,
    script_hash: bytes | None,
    pointer: CardanoBlockchainPointerType | None,
) -> list[PropertyType]:
    if path:
        return [(None, address_n_to_str(path))]
    elif key_hash:
        return [(None, key_hash)]
    elif script_hash:
        return [(None, format_script_hash(script_hash))]
    elif pointer:
        return [
            ("Block: %s" % pointer.block_index, None),
            ("Transaction: %s" % pointer.tx_index, None),
            ("Certificate: %s" % pointer.certificate_index, None),
        ]

    raise ValueError("Invalid credential")


def get_public_key_hash(keychain: seed.Keychain, path: list[int]) -> bytes:
    public_key = derive_public_key(keychain, path)
    return hashlib.blake2b(data=public_key, outlen=ADDRESS_KEY_HASH_SIZE).digest()


def derive_public_key(
    keychain: seed.Keychain, path: list[int], extended: bool = False
) -> bytes:
    node = keychain.derive(path)
    public_key = remove_ed25519_prefix(node.public_key())
    return public_key if not extended else public_key + node.chain_code()


def validate_stake_credential(
    path: list[int],
    script_hash: bytes | None,
    signing_mode: CardanoTxSigningMode,
    error: wire.ProcessError,
) -> None:
    if path and script_hash:
        raise error

    if path:
        if signing_mode != CardanoTxSigningMode.ORDINARY_TRANSACTION:
            raise error
        if not SCHEMA_STAKING_ANY_ACCOUNT.match(path):
            raise error
    elif script_hash:
        if signing_mode != CardanoTxSigningMode.MULTISIG_TRANSACTION:
            raise error
        if len(script_hash) != SCRIPT_HASH_SIZE:
            raise error
    else:
        raise error
