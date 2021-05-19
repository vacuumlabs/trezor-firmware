# Automatically generated by pb2py
# fmt: off
# isort:skip_file
from .. import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
        EnumTypeCardanoScriptType = Literal[0, 1, 2, 3, 4, 5]
    except ImportError:
        pass


class CardanoScriptT(p.MessageType):

    def __init__(
        self,
        *,
        type: EnumTypeCardanoScriptType,
        scripts: Optional[List['CardanoScriptT']] = None,
        key_path: Optional[List[int]] = None,
        key_hash: Optional[bytes] = None,
        required: Optional[int] = None,
        invalid_before: Optional[int] = None,
        invalid_hereafter: Optional[int] = None,
    ) -> None:
        self.scripts = scripts if scripts is not None else []
        self.key_path = key_path if key_path is not None else []
        self.type = type
        self.key_hash = key_hash
        self.required = required
        self.invalid_before = invalid_before
        self.invalid_hereafter = invalid_hereafter

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('type', p.EnumType("CardanoScriptType", (0, 1, 2, 3, 4, 5,)), p.FLAG_REQUIRED),
            2: ('scripts', CardanoScriptT, p.FLAG_REPEATED),
            3: ('key_hash', p.BytesType, None),
            4: ('key_path', p.UVarintType, p.FLAG_REPEATED),
            5: ('required', p.UVarintType, None),
            6: ('invalid_before', p.UVarintType, None),
            7: ('invalid_hereafter', p.UVarintType, None),
        }
