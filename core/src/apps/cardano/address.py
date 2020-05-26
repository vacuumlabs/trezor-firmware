from trezor import wire
from trezor.crypto import hashlib
from trezor.messages import CardanoAddressType

import apps.cardano.address_id as AddressId
from apps.cardano import BYRON_PURPOSE, CURVE, SHELLEY_PURPOSE
from apps.cardano.bech32 import bech32_encode
from apps.cardano.bootstrap_address import derive_address_and_node
from apps.cardano.utils import variable_length_encode
from apps.common import HARDENED, paths
from apps.common.seed import remove_ed25519_prefix

if False:
    from trezor.messages.CardanoGetAddress import CardanoGetAddress
    from apps.cardano import seed


def validate_full_path(path: list) -> bool:
    """
    Validates derivation path to fit {44', 1852'}/1815'/a'/{0,1}/i,
    where `a` is an account number and i an address index.
    The max value for `a` is 20, 1 000 000 for `i`.
    """
    if len(path) != 5:
        return False
    if path[0] != BYRON_PURPOSE and path[0] != SHELLEY_PURPOSE:
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


async def validate_address_path(ctx: wire.Context, msg: CardanoGetAddress, keychain: seed.Keychain) -> None:
    # TODO what does this do? should we call it somewhere for validation of staking key paths, too?
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)


def get_human_readable_address(address: bytes) -> str:
    return bech32_encode("addr", address)


def get_base_address(
    keychain: seed.Keychain, path: list, network_id: int, staking_key_hash: bytes
) -> str:
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for base address")

    spending_part = _get_spending_part(keychain, path)

    if staking_key_hash is None:
        staking_path = _path_to_staking_path(path)
        staking_node = keychain.derive(staking_path)
        staking_key = remove_ed25519_prefix(staking_node.public_key())
        staking_part = hashlib.blake2b(data=staking_key, outlen=28).digest()
    else:
        staking_part = staking_key_hash

    address_header = _get_address_header(CardanoAddressType.BASE_ADDRESS, network_id)
    address = address_header + spending_part + staking_part

    return get_human_readable_address(address)


def get_pointer_address(
    keychain: seed.Keychain,
    path: list,
    network_id: int,
    block_index: int,
    tx_index: int,
    certificate_index: int,
) -> str:
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for pointer address")

    spending_part = _get_spending_part(keychain, path)

    address_header = _get_address_header(CardanoAddressType.POINTER_ADDRESS, network_id)
    encoded_pointer = _encode_pointer(block_index, tx_index, certificate_index)
    address = address_header + spending_part + encoded_pointer

    return get_human_readable_address(address)


def get_enterprise_address(keychain: seed.Keychain, path: list, network_id: int) -> str:
    if not _validate_shelley_address_path(path):
        raise wire.DataError("Invalid path for enterprise address")

    spending_part = _get_spending_part(keychain, path)

    address_header = _get_address_header(
        CardanoAddressType.ENTERPRISE_ADDRESS, network_id
    )
    address = address_header + spending_part

    return get_human_readable_address(address)


def get_bootstrap_address(keychain: seed.Keychain, path: list) -> str:
    if not _validate_bootstrap_address_path(path):
        raise wire.DataError("Invalid path for bootstrap address")

    address, _ = derive_address_and_node(keychain, path)
    return address


def _validate_shelley_address_path(path: list) -> bool:
    return path[0] == SHELLEY_PURPOSE


def _validate_bootstrap_address_path(path: list) -> bool:
    return path[0] == BYRON_PURPOSE


def _get_spending_part(keychain: seed.Keychain, path: list) -> bytes:
    spending_node = keychain.derive(path)
    spending_key = remove_ed25519_prefix(spending_node.public_key())
    return hashlib.blake2b(data=spending_key, outlen=28).digest()


def _path_to_staking_path(path: list) -> list:
    return path[:3] + [2, 0]


def _get_address_header(address_type: int, network_id: int) -> bytes:
    if address_type == CardanoAddressType.BOOTSTRAP_ADDRESS:
        """
        Bootstrap addresses don't have an explicit header in the Shelley
        spec. However, thanks to their CBOR structure they always start with
        0b1000 - the bootstrap address id. This is no coincidence.
        The Shelley address headers are purposefully built around these
        starting bits of the bootstrap address.
        """
        raise ValueError("Bootstrap address does not contain an explicit header")

    address_id = _get_address_id(address_type)
    header = address_id << 4 | network_id

    return bytes([header])


def _get_address_id(address_type: int) -> int:
    # todo: GK - script combinations
    if address_type == CardanoAddressType.BASE_ADDRESS:
        address_id = AddressId.BASE_ADDRESS_KEY_KEY
    elif address_type == CardanoAddressType.POINTER_ADDRESS:
        address_id = AddressId.POINTER_ADDRESS_KEY
    elif address_type == CardanoAddressType.ENTERPRISE_ADDRESS:
        address_id = AddressId.ENTERPRISE_ADDRESS_KEY
    elif address_type == CardanoAddressType.BOOTSTRAP_ADDRESS:
        address_id = AddressId.BOOTSTRAP_ADDRESS_ID
    else:
        raise wire.DataError("Invalid address type")

    return address_id


def _encode_pointer(block_index: int, tx_index: int, certificate_index: int) -> bytes:
    block_index_encoded = variable_length_encode(block_index)
    tx_index_encoded = variable_length_encode(tx_index)
    certificate_index_encoded = variable_length_encode(certificate_index)

    return bytes(block_index_encoded + tx_index_encoded + certificate_index_encoded)
