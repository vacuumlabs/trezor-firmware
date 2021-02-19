# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class CardanoSignedTx(p.MessageType):
    MESSAGE_WIRE_TYPE = 310

    def __init__(
        self,
        *,
        tx_hash: bytes,
        serialized_tx: bytes,
        expect_more_chunks: bool = None,
    ) -> None:
        self.tx_hash = tx_hash
        self.serialized_tx = serialized_tx
        self.expect_more_chunks = expect_more_chunks

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('tx_hash', p.BytesType, p.FLAG_REQUIRED),
            2: ('serialized_tx', p.BytesType, p.FLAG_REQUIRED),
            3: ('expect_more_chunks', p.BoolType, None),
        }
