from trezor import wire
from trezor.enums import CardanoCertificateType
from trezor.messages import (
    CardanoSignTxInit,
    CardanoTxCertificate,
    CardanoTxOutput,
    CardanoTxWitnessRequest,
)

from .. import seed
from ..helpers import (
    INVALID_CERTIFICATE,
    INVALID_OUTPUT,
    INVALID_STAKE_POOL_REGISTRATION_TX_STRUCTURE,
    INVALID_STAKEPOOL_REGISTRATION_TX_WITNESSES,
    INVALID_TX_SIGNING_REQUEST,
)
from ..helpers.paths import SCHEMA_STAKING_ANY_ACCOUNT
from ..layout import confirm_stake_pool_registration_final
from .signer import Signer


class PoolOwnerSigner(Signer):
    """
    We have a separate tx signing flow for stake pool registration because it's a
    transaction where the witnessable entries (i.e. inputs, withdrawals, etc.) are not
    supposed to be controlled by the HW wallet, which means the user is vulnerable to
    unknowingly supplying a witness for an UTXO or other tx entry they think is external,
    resulting in the co-signers gaining control over their funds (Something SLIP-0019 is
    dealing with for BTC but no similar standard is currently available for Cardano).
    Hence we completely forbid witnessing inputs and other entries of the transaction
    except the stake pool certificate itself and we provide a witness only to the user's
    staking key in the list of pool owners.
    """

    def __init__(
        self, ctx: wire.Context, msg: CardanoSignTxInit, keychain: seed.Keychain
    ) -> None:
        super().__init__(ctx, msg, keychain)

    def _validate_tx_signing_request(self) -> None:
        super()._validate_tx_signing_request()
        if (
            self.msg.certificates_count != 1
            or self.msg.withdrawals_count != 0
            or self.msg.minting_asset_groups_count != 0
        ):
            raise INVALID_STAKE_POOL_REGISTRATION_TX_STRUCTURE

        if (
            self.msg.script_data_hash is not None
            or self.msg.collateral_inputs_count != 0
            or self.msg.required_signers_count != 0
        ):
            raise INVALID_TX_SIGNING_REQUEST

    async def _confirm_transaction(self, tx_hash: bytes) -> None:
        # super() omitted intentionally
        await confirm_stake_pool_registration_final(
            self.ctx,
            self.msg.protocol_magic,
            self.msg.ttl,
            self.msg.validity_interval_start,
        )

    def _validate_output(self, output: CardanoTxOutput) -> None:
        super()._validate_output(output)
        if output.address_parameters is not None:
            raise INVALID_OUTPUT
        if output.datum_hash is not None:
            raise INVALID_OUTPUT

    def _should_show_output(self, output: CardanoTxOutput) -> bool:
        # super() omitted intentionally
        # There are no spending witnesses, it is thus safe to hide outputs.
        return False

    def _validate_certificate(self, certificate: CardanoTxCertificate) -> None:
        super()._validate_certificate(certificate)
        if certificate.type != CardanoCertificateType.STAKE_POOL_REGISTRATION:
            raise INVALID_CERTIFICATE

    def _validate_witness_request(
        self, witness_request: CardanoTxWitnessRequest
    ) -> None:
        super()._validate_witness_request(witness_request)
        if not SCHEMA_STAKING_ANY_ACCOUNT.match(witness_request.path):
            raise INVALID_STAKEPOOL_REGISTRATION_TX_WITNESSES

    def _is_network_id_verifiable(self) -> bool:
        # super() omitted intentionally
        return True
