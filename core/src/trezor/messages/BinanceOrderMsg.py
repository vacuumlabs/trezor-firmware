# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
        EnumTypeBinanceOrderType = Literal[0, 1, 2, 3]
        EnumTypeBinanceOrderSide = Literal[0, 1, 2]
        EnumTypeBinanceTimeInForce = Literal[0, 1, 2, 3]
    except ImportError:
        pass


class BinanceOrderMsg(p.MessageType):
    MESSAGE_WIRE_TYPE = 707

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        ordertype: Optional[EnumTypeBinanceOrderType] = None,
        price: Optional[int] = None,
        quantity: Optional[int] = None,
        sender: Optional[str] = None,
        side: Optional[EnumTypeBinanceOrderSide] = None,
        symbol: Optional[str] = None,
        timeinforce: Optional[EnumTypeBinanceTimeInForce] = None,
    ) -> None:
        self.id = id
        self.ordertype = ordertype
        self.price = price
        self.quantity = quantity
        self.sender = sender
        self.side = side
        self.symbol = symbol
        self.timeinforce = timeinforce

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('id', p.UnicodeType, None),
            2: ('ordertype', p.EnumType("BinanceOrderType", (0, 1, 2, 3,)), None),
            3: ('price', p.SVarintType, None),
            4: ('quantity', p.SVarintType, None),
            5: ('sender', p.UnicodeType, None),
            6: ('side', p.EnumType("BinanceOrderSide", (0, 1, 2,)), None),
            7: ('symbol', p.UnicodeType, None),
            8: ('timeinforce', p.EnumType("BinanceTimeInForce", (0, 1, 2, 3,)), None),
        }
