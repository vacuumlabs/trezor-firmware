# Automatically generated by pb2py
# fmt: off
# isort:skip_file
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class MoneroMultisigKLRki(p.MessageType):

    def __init__(
        self,
        *,
        K: Optional[bytes] = None,
        L: Optional[bytes] = None,
        R: Optional[bytes] = None,
        ki: Optional[bytes] = None,
    ) -> None:
        self.K = K
        self.L = L
        self.R = R
        self.ki = ki

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('K', p.BytesType, None),
            2: ('L', p.BytesType, None),
            3: ('R', p.BytesType, None),
            4: ('ki', p.BytesType, None),
        }
