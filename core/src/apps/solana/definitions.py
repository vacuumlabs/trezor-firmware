from typing import TYPE_CHECKING

from trezor.enums import SolanaTokenStandard
from trezor.messages import SolanaTokenInfo

if TYPE_CHECKING:
    from typing_extensions import Self


class Definitions:
    """Class that holds Solana definitions - network and tokens.
    Prefers built-in definitions over encoded ones.
    """

    def __init__(self, tokens: dict[bytes, SolanaTokenInfo]) -> None:
        self._tokens = tokens

    @classmethod
    def from_encoded(
        cls,
        encoded_token: bytes | None,
    ) -> Self:
        from apps.common import definitions

        tokens: dict[bytes, SolanaTokenInfo] = {}

        # get token definition
        if encoded_token is not None:
            token = definitions.decode_definition(encoded_token, SolanaTokenInfo)
            tokens[token.address] = token

        return cls(tokens)

    def get_token(self, address: bytes) -> SolanaTokenInfo:
        # NOTE: there are currently to additional built-in definitions
        if address in self._tokens:
            return self._tokens[address]

        return SolanaTokenInfo(
            name="Unknown token",
            ticker="UNKN",
            address=b"",
            standard=SolanaTokenStandard.SPL,
            decimals=0,
        )
