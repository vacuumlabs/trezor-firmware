# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

from .MoneroMultisigKLRki import MoneroMultisigKLRki
from .MoneroOutputEntry import MoneroOutputEntry

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class MoneroTransactionSourceEntry(p.MessageType):

    def __init__(
        self,
        *,
        outputs: Optional[List[MoneroOutputEntry]] = None,
        real_out_additional_tx_keys: Optional[List[bytes]] = None,
        real_output: Optional[int] = None,
        real_out_tx_key: Optional[bytes] = None,
        real_output_in_tx_index: Optional[int] = None,
        amount: Optional[int] = None,
        rct: Optional[bool] = None,
        mask: Optional[bytes] = None,
        multisig_kLRki: Optional[MoneroMultisigKLRki] = None,
        subaddr_minor: Optional[int] = None,
    ) -> None:
        self.outputs = outputs if outputs is not None else []
        self.real_out_additional_tx_keys = real_out_additional_tx_keys if real_out_additional_tx_keys is not None else []
        self.real_output = real_output
        self.real_out_tx_key = real_out_tx_key
        self.real_output_in_tx_index = real_output_in_tx_index
        self.amount = amount
        self.rct = rct
        self.mask = mask
        self.multisig_kLRki = multisig_kLRki
        self.subaddr_minor = subaddr_minor

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('outputs', MoneroOutputEntry, p.FLAG_REPEATED),
            2: ('real_output', p.UVarintType, None),
            3: ('real_out_tx_key', p.BytesType, None),
            4: ('real_out_additional_tx_keys', p.BytesType, p.FLAG_REPEATED),
            5: ('real_output_in_tx_index', p.UVarintType, None),
            6: ('amount', p.UVarintType, None),
            7: ('rct', p.BoolType, None),
            8: ('mask', p.BytesType, None),
            9: ('multisig_kLRki', MoneroMultisigKLRki, None),
            10: ('subaddr_minor', p.UVarintType, None),
        }
