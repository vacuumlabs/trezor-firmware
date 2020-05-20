# Automatically generated by pb2py
# fmt: off
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
        EnumTypeCardanoAddressType = Literal[0, 1, 2, 3]
    except ImportError:
        pass


class CardanoGetAddress(p.MessageType):
    MESSAGE_WIRE_TYPE = 307

    def __init__(
        self,
        address_n: List[int] = None,
        show_display: bool = None,
        address_type: EnumTypeCardanoAddressType = None,
        network_id: int = None,
        block_index: int = None,
        tx_index: int = None,
        certificate_index: int = None,
    ) -> None:
        self.address_n = address_n if address_n is not None else []
        self.show_display = show_display
        self.address_type = address_type
        self.network_id = network_id
        self.block_index = block_index
        self.tx_index = tx_index
        self.certificate_index = certificate_index

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('address_n', p.UVarintType, p.FLAG_REPEATED),
            2: ('show_display', p.BoolType, 0),
            3: ('address_type', p.EnumType("CardanoAddressType", (0, 1, 2, 3)), 0),
            4: ('network_id', p.UVarintType, 0),
            5: ('block_index', p.UVarintType, 0),
            6: ('tx_index', p.UVarintType, 0),
            7: ('certificate_index', p.UVarintType, 0),
        }
