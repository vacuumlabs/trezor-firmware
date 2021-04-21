# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class EosActionVoteProducer(p.MessageType):

    def __init__(
        self,
        *,
        producers: Optional[List[int]] = None,
        voter: Optional[int] = None,
        proxy: Optional[int] = None,
    ) -> None:
        self.producers = producers if producers is not None else []
        self.voter = voter
        self.proxy = proxy

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('voter', p.UVarintType, None),
            2: ('proxy', p.UVarintType, None),
            3: ('producers', p.UVarintType, p.FLAG_REPEATED),
        }
