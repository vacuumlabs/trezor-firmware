# Automatically generated by pb2py
# fmt: off
import protobuf as p

from .CardanoAddressParametersType import CardanoAddressParametersType

if __debug__:
    try:
        from typing import Dict, List  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class CardanoGetAddress(p.MessageType):
    MESSAGE_WIRE_TYPE = 307

    def __init__(
        self,
        address_parameters: CardanoAddressParametersType = None,
        show_display: bool = None,
        network_id: int = None,
    ) -> None:
        self.address_parameters = address_parameters
        self.show_display = show_display
        self.network_id = network_id

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('address_parameters', CardanoAddressParametersType, 0),
            2: ('show_display', p.BoolType, 0),
            3: ('network_id', p.UVarintType, 0),
        }
