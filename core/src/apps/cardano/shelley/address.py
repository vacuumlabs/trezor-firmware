from trezor.crypto import bech32, hashlib

from apps.common import HARDENED
from apps.common.seed import remove_ed25519_prefix
from apps.cardano.shelley import CURVE
from apps.common import paths


def validate_full_path(path: list) -> bool:
    """
    Validates derivation path to fit 1852'/1815'/a'/{0,1}/i,
    where `a` is an account number and i an address index.
    The max value for `a` is 20, 1 000 000 for `i`.
    """
    if len(path) != 5:
        return False
    if path[0] != 1852 | HARDENED:
        return False
    if path[1] != 1815 | HARDENED:
        return False
    if path[2] < HARDENED or path[2] > 20 | HARDENED:  # TODO do we still limit it to 20 accounts?
        return False
    if path[3] != 0 and path[3] != 1:
        return False
    if path[4] > 1000000:  # TODO do we still impose this?
        return False
    return True


async def validate_address_path(ctx, msg, keychain):
    # TODO what does this do? should we call it somewhere for validation of staking key paths, too?
    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)


def address_bytes(keychain, path: list):
    # TODO incomplete
    spending_node = keychain.derive(path)
    spending_key = remove_ed25519_prefix(spending_node.public_key)  # not sure if remove_ed25519_prefix should be used
    spending_part = hashlib.blake2b(data=spending_key, outlen=28).digest()

    staking_path = path[:3]
    staking_path.append([2, 0])
    staking_node = keychain.derive(staking_path)
    staking_key = remove_ed25519_prefix(staking_node.public_key)  # not sure if remove_ed25519_prefix should be used
    staking_part = hashlib.blake2b(data=staking_key, outlen=28).digest()

    return spending_part + staking_part


def address_human(keychain, path: list):
    addr = address_bytes(keychain, path)
    convertedbits = bech32.convertbits(addr, 8, 5)
    return bech32.bech32_encode("ca", convertedbits)
