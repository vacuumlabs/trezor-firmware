from trezor import wire
from trezor.crypto import hashlib
from trezor.messages import CardanoAddressType

from apps.cardano.shelley import CURVE
from apps.cardano.shelley.bech32 import bech32_encode
from apps.cardano.shelley.bootstrap_address import derive_address_and_node
from apps.cardano.shelley.utils import variable_length_encode
from apps.common import HARDENED, paths
from apps.common.seed import remove_ed25519_prefix


def validate_full_path(path: list) -> bool:
    """
    Validates derivation path to fit {44', 1852'}/1815'/a'/{0,1}/i,
    where `a` is an account number and i an address index.
    The max value for `a` is 20, 1 000 000 for `i`.
    """
    if len(path) != 5:
        return False
    if path[0] != 44 | HARDENED and path[0] != 1852 | HARDENED:
        return False
    if path[1] != 1815 | HARDENED:
        return False
    if (
        path[2] < HARDENED or path[2] > 20 | HARDENED
    ):  # TODO do we still limit it to 20 accounts?
        return False
    if path[3] != 0 and path[3] != 1:
        return False
    if path[4] > 1000000:  # TODO do we still impose this?
        return False
    return True


async def validate_address_path(ctx, msg, keychain):
    # TODO what does this do? should we call it somewhere for validation of staking key paths, too?
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)


def get_human_readable_address(address):
    return bech32_encode("addr", address)


def get_base_address(keychain, path: list, network_id):
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for base address")

    spending_part = _get_spending_part(keychain, path)

    staking_path = _path_to_staking_path(path)
    staking_node = keychain.derive(staking_path)
    staking_key = remove_ed25519_prefix(staking_node.public_key())
    staking_part = hashlib.blake2b(data=staking_key, outlen=28).digest()

    address_header = _get_address_header(CardanoAddressType.BASE_ADDRESS, network_id)
    address = address_header + spending_part + staking_part

    return get_human_readable_address(address)


def get_pointer_address(
    keychain, path: list, network_id, block_index, tx_index, certificate_index
):
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for pointer address")

    spending_part = _get_spending_part(keychain, path)

    address_header = _get_address_header(CardanoAddressType.POINTER_ADDRESS, network_id)
    encoded_pointer = _encode_pointer(block_index, tx_index, certificate_index)
    address = address_header + spending_part + encoded_pointer

    return get_human_readable_address(address)


def get_enterprise_address(keychain, path: list, network_id):
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for enterprise address")

    spending_part = _get_spending_part(keychain, path)

    address_header = _get_address_header(
        CardanoAddressType.ENTERPRISE_ADDRESS, network_id
    )
    address = address_header + spending_part

    return get_human_readable_address(address)


def get_bootstrap_address(keychain, path: list):
    if not _validate_bootstrap_address_path(path):
        raise wire.DataError("Invalid path for bootstrap address")

    return derive_address_and_node(keychain, path)


def _validate_shelley_address_path(path: list) -> bool:
    return path[0] == 1852 | HARDENED


def _validate_bootstrap_address_path(path: list) -> bool:
    return path[0] == 44 | HARDENED


def _get_spending_part(keychain, path):
    spending_node = keychain.derive(path)
    spending_key = remove_ed25519_prefix(spending_node.public_key())
    return hashlib.blake2b(data=spending_key, outlen=28).digest()


def _path_to_staking_path(path):
    return path[:3] + [2, 0]


def _get_address_header(address_type, network_id):
    # todo: GK - script and other addresses
    if address_type == CardanoAddressType.BASE_ADDRESS:
        header = network_id
    elif address_type == CardanoAddressType.POINTER_ADDRESS:
        header = (4 << 4) | network_id
    elif address_type == CardanoAddressType.ENTERPRISE_ADDRESS:
        header = (6 << 4) | network_id
    elif address_type == CardanoAddressType.BOOTSTRAP_ADDRESS:
        header = (8 << 4) | network_id
    else:
        raise wire.DataError("Invalid address type")

    return bytes([header])


def _encode_pointer(block_index, tx_index, certificate_index):
    block_index = variable_length_encode(block_index)
    tx_index = variable_length_encode(tx_index)
    certificate_index = variable_length_encode(certificate_index)

    return bytes(block_index + tx_index + certificate_index)
