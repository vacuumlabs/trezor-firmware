import storage
from storage import cache
from trezor import wire
from trezor.crypto import bip32

from apps.cardano import BYRON_SEED_NAMESPACE, CURVE, SHELLEY_SEED_NAMESPACE
from apps.common import mnemonic
from apps.common.passphrase import get as get_passphrase

BYRON_ROOT_DICT_KEY = 0
SHELLEY_ROOT_DICT_KEY = 1


class Keychain:
    def __init__(self, path: list, root: bip32.HDNode):
        self.path = path
        self.root = root

    def validate_path(self, checked_path: list, checked_curve: str):
        if checked_curve != CURVE:
            raise wire.DataError("Forbidden key path")
        if (
            checked_path[:2] != SHELLEY_SEED_NAMESPACE
            and checked_path[:2] != BYRON_SEED_NAMESPACE
        ):
            raise wire.DataError("Forbidden key path")

    def derive(self, node_path: list) -> bip32.HDNode:
        # check we are in the cardano namespace
        prefix = node_path[: len(self.path)]
        suffix = node_path[len(self.path) :]
        if prefix != self.path:
            raise wire.DataError("Forbidden key path")
        # derive child node from the root
        node = self.root.clone()
        for i in suffix:
            node.derive_cardano(i)
        return node


async def get_keychain(ctx: wire.Context, namespace) -> Keychain:
    root = _get_root_from_cache(namespace)

    if not storage.is_initialized():
        raise wire.NotInitialized("Device is not initialized")

    if root is None:
        passphrase = await get_passphrase(ctx)
        if mnemonic.is_bip39():
            # derive the root node from mnemonic and passphrase
            root = bip32.from_mnemonic_cardano(
                mnemonic.get_secret().decode(), passphrase
            )
        else:
            seed = mnemonic.get_seed(passphrase)
            root = bip32.from_seed(seed, "ed25519 cardano seed")

        # derive the namespaced root node
        for i in namespace:
            root.derive_cardano(i)

        _set_root_in_cache(namespace, root)

    keychain = Keychain(namespace, root)
    return keychain


def _get_root_dict_key(namespace):
    if namespace == BYRON_SEED_NAMESPACE:
        return BYRON_ROOT_DICT_KEY
    if namespace == SHELLEY_SEED_NAMESPACE:
        return SHELLEY_ROOT_DICT_KEY

    raise wire.DataError("Invalid namespace")


def _get_root_from_cache(namespace):
    roots = cache.get(cache.APP_CARDANO_ROOT)

    if roots is None:
        roots = {BYRON_ROOT_DICT_KEY: None, SHELLEY_ROOT_DICT_KEY: None}

    root_dict_key = _get_root_dict_key(namespace)
    return roots[root_dict_key]


def _set_root_in_cache(namespace, root):
    roots = cache.get(cache.APP_CARDANO_ROOT)

    root_dict_key = _get_root_dict_key(namespace)

    if roots is None:
        roots = {BYRON_ROOT_DICT_KEY: None, SHELLEY_ROOT_DICT_KEY: None}

    roots[root_dict_key] = root
    storage.cache.set(cache.APP_CARDANO_ROOT, roots)
