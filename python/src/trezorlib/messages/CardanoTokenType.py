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


class CardanoTokenType(p.MessageType):

    def __init__(
        self,
        *,
        asset_name_bytes: bytes,
        amount: Optional[int] = None,
        mint_amount: Optional[int] = None,
    ) -> None:
        self.asset_name_bytes = asset_name_bytes
        self.amount = amount
        self.mint_amount = mint_amount

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('asset_name_bytes', p.BytesType, p.FLAG_REQUIRED),
            2: ('amount', p.UVarintType, None),
            3: ('mint_amount', p.SVarintType, None),
        }
