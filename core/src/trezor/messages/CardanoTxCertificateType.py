# Automatically generated by pb2py
# fmt: off
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class CardanoTxCertificateType(p.MessageType):

    def __init__(
        self,
        type: int = None,
        path: List[int] = None,
        pool: bytes = None,
    ) -> None:
        self.type = type
        self.path = path if path is not None else []
        self.pool = pool

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('type', p.UVarintType, 0),
            2: ('path', p.UVarintType, p.FLAG_REPEATED),
            3: ('pool', p.BytesType, 0),
        }
