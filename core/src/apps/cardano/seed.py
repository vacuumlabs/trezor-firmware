from storage import cache, device
from trezor import wire
from trezor.crypto import bip32

from apps.cardano import SEED_NAMESPACE_BYRON, SEED_NAMESPACE_SHELLEY
from apps.common import mnemonic
from apps.common.passphrase import get as get_passphrase

if False:
    from typing import Tuple

    from apps.common.seed import Bip32Path, MsgIn, MsgOut, Handler, HandlerWithKeychain


class Keychain:
    """Cardano keychain hard-coded to SEED_NAMESPACE_BYRON and SEED_NAMESPACE_SHELLEY."""

    def __init__(self, root: bip32.HDNode) -> None:
        self.root = root
        self.byron_root = None
        self.shelley_root = None

        self.byron_namespace_length = len(SEED_NAMESPACE_BYRON)
        self.shelley_namespace_length = len(SEED_NAMESPACE_SHELLEY)

    def _is_byron_path(self, path: Bip32Path):
        return path[: self.byron_namespace_length] == SEED_NAMESPACE_BYRON

    def _is_shelley_path(self, path: Bip32Path):
        return path[: self.shelley_namespace_length] == SEED_NAMESPACE_SHELLEY

    def match_path(self, path: Bip32Path) -> Tuple[int, Bip32Path]:
        if self._is_byron_path(path):
            return 0, path[self.byron_namespace_length :]
        elif self._is_shelley_path(path):
            return 0, path[self.shelley_namespace_length :]
        else:
            raise wire.DataError("Forbidden key path")        

    def _create_namespace_root(self, namespace: list):
        new_root = self.root.clone()
        for i in namespace:
            new_root.derive_cardano(i)

        return new_root

    def _get_path_root(self, path: list):
        if self._is_byron_path(path):
            if self.byron_root is None:
                self.byron_root = self._create_namespace_root(SEED_NAMESPACE_BYRON)
            root = self.byron_root
        elif self._is_shelley_path(path):
            if self.shelley_root is None:
                self.shelley_root = self._create_namespace_root(SEED_NAMESPACE_SHELLEY)
            root = self.shelley_root
        else:
            raise wire.DataError("Forbidden key path")

        return root

    def derive(self, node_path: Bip32Path) -> bip32.HDNode:
        _, suffix = self.match_path(node_path)

        path_root = self._get_path_root(node_path)

        # derive child node from the root
        node = path_root.clone()
        for i in suffix:
            node.derive_cardano(i)
        return node

    # XXX the root node remains in session cache so we should not delete it
    # def __del__(self) -> None:
    #     self.root.__del__()


@cache.stored_async(cache.APP_CARDANO_ROOT)
async def get_keychain(ctx: wire.Context) -> Keychain:
    if not device.is_initialized():
        raise wire.NotInitialized("Device is not initialized")

    passphrase = await get_passphrase(ctx)
    if mnemonic.is_bip39():
        # derive the root node from mnemonic and passphrase via Cardano Icarus algorithm
        root = bip32.from_mnemonic_cardano(mnemonic.get_secret().decode(), passphrase)
    else:
        # derive the root node via SLIP-0023
        seed = mnemonic.get_seed(passphrase)
        root = bip32.from_seed(seed, "ed25519 cardano seed")

    keychain = Keychain(root)
    return keychain


def with_keychain(func: HandlerWithKeychain[MsgIn, MsgOut]) -> Handler[MsgIn, MsgOut]:
    async def wrapper(ctx: wire.Context, msg: MsgIn) -> MsgOut:
        keychain = await get_keychain(ctx)
        return await func(ctx, msg, keychain)

    return wrapper
