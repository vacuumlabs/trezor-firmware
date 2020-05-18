from trezor import wire
from trezor.messages import MessageType
from apps.common import HARDENED


CURVE = "ed25519"

BYRON_SEED_NAMESPACE = [44 | HARDENED, 1815 | HARDENED]
SHELLEY_SEED_NAMESPACE = [1852 | HARDENED, 1815 | HARDENED]


def boot() -> None:
    wire.add(MessageType.CardanoGetAddress, __name__, "get_address")
    wire.add(MessageType.CardanoGetPublicKey, __name__, "get_public_key")
    wire.add(MessageType.CardanoSignTx, __name__, "sign_tx")
