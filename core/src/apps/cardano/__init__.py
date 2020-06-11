from micropython import const

from trezor import wire
from trezor.messages import MessageType

from apps.common import HARDENED

CURVE = "ed25519"

BYRON_PURPOSE = 44 | HARDENED
SHELLEY_PURPOSE = 1852 | HARDENED

SEED_NAMESPACE_BYRON = [BYRON_PURPOSE, 1815 | HARDENED]
SEED_NAMESPACE_SHELLEY = [SHELLEY_PURPOSE, 1815 | HARDENED]


def boot() -> None:
    wire.add(MessageType.CardanoGetAddress, __name__, "get_address")
    wire.add(MessageType.CardanoGetPublicKey, __name__, "get_public_key")
    wire.add(MessageType.CardanoSignTx, __name__, "sign_tx")
