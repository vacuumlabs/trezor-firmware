from micropython import const
from ubinascii import unhexlify

from trezor import log, wire
from trezor.crypto import base58, hashlib
from trezor.crypto.curve import ed25519
from trezor.messages import CardanoCertificateType
from trezor.messages.CardanoSignedTx import CardanoSignedTx

from apps.cardano import CURVE, seed
from apps.cardano.address import derive_address, validate_full_path
from apps.cardano.bootstrap_address import is_safe_output_address
from apps.cardano.layout import (
    confirm_certificate,
    confirm_sending,
    confirm_transaction,
)
from apps.common import cbor
from apps.common.paths import validate_path
from apps.common.seed import remove_ed25519_prefix

if False:
    from typing import List, Tuple
    from trezor import wire
    from trezor.messages.CardanoTxCertificateType import CardanoTxCertificateType
    from trezor.messages.CardanoSignTx import CardanoSignTx
    from trezor.messages.CardanoTxInputType import CardanoTxInputType
    from trezor.messages.CardanoTxOutputType import CardanoTxOutputType

# the maximum allowed change address.  this should be large enough for normal
# use and still allow to quickly brute-force the correct bip32 path
MAX_CHANGE_ADDRESS_INDEX = const(1000000)
ACCOUNT_PREFIX_DEPTH = const(2)

KNOWN_PROTOCOL_MAGICS = {764824073: "Mainnet", 1097911063: "Testnet"}


# we consider addresses from the external chain as possible change addresses as well
def is_change(output: List[int], inputs: List[CardanoTxInputType]) -> bool:
    for input in inputs:
        inp = input.address_n
        if (
            not output[:ACCOUNT_PREFIX_DEPTH] == inp[:ACCOUNT_PREFIX_DEPTH]
            or not output[-2] < 2
            or not output[-1] < MAX_CHANGE_ADDRESS_INDEX
        ):
            return False
    return True


async def show_tx(
    ctx: wire.Context,
    outputs: list,
    outcoins: list,
    fee: int,
    network_name: str,
    raw_inputs: List[CardanoTxInputType],
    raw_outputs: List[CardanoTxOutputType],
    certificates: List[CardanoTxCertificateType],
) -> None:
    for index, output in enumerate(outputs):
        if raw_outputs[index].address_parameters and is_change(
            raw_outputs[index].address_parameters.address_n, raw_inputs
        ):
            continue

        await confirm_sending(ctx, outcoins[index], output)

    for certificate in certificates:
        await confirm_certificate(ctx, certificate)

    total_amount = sum(outcoins)
    await confirm_transaction(ctx, total_amount, fee, network_name, certificates)


@seed.with_keychain
async def sign_tx(
    ctx: wire.Context, msg: CardanoSignTx, keychain: seed.Keychain
) -> CardanoSignedTx:
    try:
        transaction = Transaction(
            msg.inputs,
            msg.outputs,
            keychain,
            msg.protocol_magic,
            msg.fee,
            msg.ttl,
            msg.certificates,
        )

        for i in msg.inputs:
            await validate_path(ctx, validate_full_path, keychain, i.address_n, CURVE)

        # sign the transaction bundle and prepare the result
        tx_body, tx_hash = transaction.serialise_tx()
        tx = CardanoSignedTx(tx_body=tx_body, tx_hash=tx_hash)

    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Signing failed")

    # display the transaction in UI
    await show_tx(
        ctx,
        transaction.output_addresses,
        transaction.outgoing_coins,
        transaction.fee,
        transaction.network_name,
        transaction.inputs,
        transaction.outputs,
        transaction.certificates,
    )

    return tx


class Transaction:
    def __init__(
        self,
        inputs: List[CardanoTxInputType],
        outputs: List[CardanoTxOutputType],
        keychain: seed.Keychain,
        protocol_magic: int,
        fee: int,
        ttl: int,
        certificates: List[CardanoTxCertificateType],
    ) -> None:
        self.inputs = inputs
        self.outputs = outputs
        self.keychain = keychain
        self.fee = fee
        self.ttl = ttl
        self.certificates = certificates

        self.network_name = KNOWN_PROTOCOL_MAGICS.get(protocol_magic, "Unknown")
        self.protocol_magic = protocol_magic

    def _process_outputs(self) -> None:
        change_addresses = []
        change_derivation_paths = []
        output_addresses = []
        outgoing_coins = []
        change_coins = []

        for output in self.outputs:
            if output.address_parameters:
                address = derive_address(
                    self.keychain,
                    output.address_parameters,
                    self.protocol_magic,
                    human_readable=False,
                )
                change_addresses.append(address)
                change_derivation_paths.append(output.address_parameters.address_n)
                change_coins.append(output.amount)
            else:
                if output.address is None:
                    raise wire.ProcessError(
                        "Each output must have address or address_n field!"
                    )
                # todo: GK - this should be checked only with byron addresses
                # if not is_safe_output_address(output.address):
                #     raise wire.ProcessError("Invalid output address!")

                outgoing_coins.append(output.amount)
                output_addresses.append(output.address)

        self.change_addresses = change_addresses
        self.output_addresses = output_addresses
        self.outgoing_coins = outgoing_coins
        self.change_coins = change_coins
        self.change_derivation_paths = change_derivation_paths

    def _build_witness(
        self, tx_body_hash: bytes, address_path: List[int]
    ) -> List[bytes]:
        node = self.keychain.derive(address_path)
        message = b"\x58\x20" + tx_body_hash

        signature = ed25519.sign_ext(
            node.private_key(), node.private_key_ext(), message
        )

        public_key = remove_ed25519_prefix(node.public_key())

        return [public_key, signature]

    def _is_certificate_witness_required(self, certificate_type: int) -> bool:
        return certificate_type != CardanoCertificateType.STAKE_REGISTRATION

    def _build_witnesses(self, tx_aux_hash: bytes) -> List[List[bytes]]:
        witnesses = []
        for input in self.inputs:
            witness = self._build_witness(tx_aux_hash, input.address_n)
            witnesses.append(witness)

        for certificate in self.certificates:
            if not self._is_certificate_witness_required(certificate.type):
                continue

            witness = self._build_witness(tx_aux_hash, certificate.path)
            witnesses.append(witness)

        # todo: GK - resolve for reward and byron witnesses

        return witnesses

    def _validate_certificate_type(self, certificate_type: int) -> int:
        return (
            certificate_type == CardanoCertificateType.STAKE_REGISTRATION
            or certificate_type == CardanoCertificateType.STAKE_DEREGISTRATION
            or certificate_type == CardanoCertificateType.STAKE_DELEGATION
        )

    def _build_certificates(self) -> list:
        certificates_for_cbor = []
        for certificate in self.certificates:
            if not self._validate_certificate_type(certificate.type):
                raise ValueError("Unsupported certificate type '%s'" % certificate.type)

            node = self.keychain.derive(certificate.path)
            public_key_hash = hashlib.blake2b(
                data=remove_ed25519_prefix(node.public_key()), outlen=28
            ).digest()

            # todo: GK - 0 deppends on cert type
            stake_credential = [0, public_key_hash]
            certificate_for_cbor = [certificate.type, stake_credential]
            if certificate.type == CardanoCertificateType.STAKE_DELEGATION:
                certificate_for_cbor.append(certificate.pool)

            certificates_for_cbor.append(certificate_for_cbor)

        return certificates_for_cbor

    def serialise_tx(self) -> Tuple[bytes, bytes]:
        self._process_outputs()

        inputs_for_cbor = []
        for input in self.inputs:
            inputs_for_cbor.append([input.prev_hash, input.prev_index])

        outputs_for_cbor = []
        for index, address in enumerate(self.output_addresses):
            outputs_for_cbor.append([unhexlify(address), self.outgoing_coins[index]])

        for index, address in enumerate(self.change_addresses):
            outputs_for_cbor.append([address, self.change_coins[index]])

        # todo: withdrawals, metadata
        tx_body = {0: inputs_for_cbor, 1: outputs_for_cbor, 2: self.fee, 3: self.ttl}

        if len(self.certificates) > 0:
            certificates_for_cbor = self._build_certificates()
            tx_body[4] = certificates_for_cbor

        tx_body_cbor = cbor.encode(tx_body)
        tx_hash = hashlib.blake2b(data=tx_body_cbor, outlen=32).digest()

        witnesses = {0: self._build_witnesses(tx_hash)}

        tx = cbor.encode([tx_body, witnesses, None])

        return tx, tx_hash
