from ubinascii import hexlify

from trezor import log, wire
from trezor.messages.CardanoPublicKey import CardanoPublicKey
from trezor.messages.HDNodeType import HDNodeType

from apps.cardano.shelley import CURVE, seed
from apps.common import HARDENED, layout, paths
from apps.common.paths import is_hardened
from apps.common.seed import remove_ed25519_prefix


async def get_public_key(ctx, msg):
    # TODO is this what we want for public staking keys as well?
    keychain = await seed.get_keychain(ctx, msg.address_n[:2])

    await paths.validate_path(
        ctx,
        _validate_path_for_get_public_key,
        keychain,
        msg.address_n,
        CURVE,
        slip44_id=1815,
    )

    try:
        key = _get_public_key(keychain, msg.address_n)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Deriving public key failed")

    if msg.show_display:
        await layout.show_pubkey(ctx, key.node.public_key)
    return key


def _get_public_key(keychain, derivation_path: list):
    node = keychain.derive(derivation_path)

    public_key = hexlify(remove_ed25519_prefix(node.public_key())).decode()
    chain_code = hexlify(node.chain_code()).decode()
    xpub_key = public_key + chain_code

    node_type = HDNodeType(
        depth=node.depth(),
        child_num=node.child_num(),
        fingerprint=node.fingerprint(),
        chain_code=node.chain_code(),
        public_key=remove_ed25519_prefix(node.public_key()),
    )

    return CardanoPublicKey(node=node_type, xpub=xpub_key)


def _validate_path_for_get_public_key(path: list, slip44_id: int) -> bool:
    """
    Checks if path has at least three hardened items and slip44 id matches.
    The path is allowed to have more than three items, but all the following
    items have to be non-hardened.

    Copied from apps.common.paths and modified to use 1852 instead of 44.
    """
    length = len(path)
    if length < 3 or length > 5:
        return False
    if path[0] != 1852 | HARDENED:  # TODO put this constant in a single place
        return False
    if path[1] != slip44_id | HARDENED:
        return False
    if path[2] < HARDENED or path[2] > 20 | HARDENED:
        return False
    if length > 3 and is_hardened(path[3]):
        return False
    if length > 4 and is_hardened(path[4]):
        return False
    return True
