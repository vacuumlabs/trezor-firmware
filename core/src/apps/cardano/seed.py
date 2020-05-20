import storage
from storage import cache
from trezor import wire
from trezor.crypto import bip32

from apps.cardano import BYRON_SEED_NAMESPACE, CURVE, SHELLEY_SEED_NAMESPACE
from apps.common import mnemonic
from apps.common.passphrase import get as get_passphrase


class Keychain:
    def __init__(self, path: list, root: bip32.HDNode):
        self.path = path
        self.root = root

    def validate_path(self, checked_path: list, checked_curve: str) -> None:
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


async def get_keychain(ctx: wire.Context, namespace: list) -> Keychain:
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


def _get_root_cache_key(namespace: list) -> int:
    if namespace == BYRON_SEED_NAMESPACE:
        return cache.APP_CARDANO_BYRON_ROOT
    elif namespace == SHELLEY_SEED_NAMESPACE:
        return cache.APP_CARDANO_SHELLEY_ROOT

    raise wire.DataError("Invalid namespace")


def _get_root_from_cache(namespace: list) -> bip32.HDNode:
    cache_key = _get_root_cache_key(namespace)
    return cache.get(cache_key)


def _set_root_in_cache(namespace: list, root: bip32.HDNode) -> None:
    cache_key = _get_root_cache_key(namespace)
    cache.set(cache_key, root)
