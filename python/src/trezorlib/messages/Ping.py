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


class Ping(p.MessageType):
    MESSAGE_WIRE_TYPE = 1

    def __init__(
        self,
        *,
        message: str = "",
        button_protection: Optional[bool] = None,
    ) -> None:
        self.message = message
        self.button_protection = button_protection

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('message', p.UnicodeType, ""),  # default=
            2: ('button_protection', p.BoolType, None),
        }
