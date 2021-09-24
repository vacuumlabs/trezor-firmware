from . import INVALID_CERTIFICATE, INVALID_STAKEPOOL_REGISTRATION_TX_WITNESS
from .paths import SCHEMA_STAKING_ANY_ACCOUNT


class PoolOwnerPathChecker:
    """
    We have a separate tx signing flow for stake pool registration because it's a
    transaction where the witnessable entries (i.e. inputs, withdrawals, etc.)
    in the transaction are not supposed to be controlled by the HW wallet, which
    means the user is vulnerable to unknowingly supplying a witness for an UTXO
    or other tx entry they think is external, resulting in the co-signers
    gaining control over their funds (Something SLIP-0019 is dealing with for
    BTC but no similar standard is currently available for Cardano). Hence we
    completely forbid witnessing inputs and other entries of the transaction
    except the stake pool certificate itself and we provide a witness only to the
    user's staking key in the list of pool owners.

    This class ensures that:
        - there is exactly one path in the pool owners list
        - the witness request path is a staking path
        - the two mentioned paths are the same
    """

    def __init__(self) -> None:
        self.path: list[int] | None = None

    def add(self, path: list[int]) -> None:
        if self.path is not None:
            raise INVALID_CERTIFICATE
        self.path = path

    def check_if_added(self) -> None:
        if self.path is None:
            raise INVALID_CERTIFICATE

    def check_witness_request(self, path: list[int]) -> None:
        if not SCHEMA_STAKING_ANY_ACCOUNT.match(path):
            raise INVALID_STAKEPOOL_REGISTRATION_TX_WITNESS
        if self.path != path:
            raise INVALID_STAKEPOOL_REGISTRATION_TX_WITNESS
