from micropython import const
from ubinascii import hexlify, unhexlify

from trezor import log, wire
from trezor.crypto import base58, hashlib
from trezor.crypto.curve import ed25519
from trezor.messages.CardanoSignedTx import CardanoSignedTx
from trezor.messages.CardanoTxAck import CardanoTxAck
from trezor.messages.CardanoTxRequest import CardanoTxRequest

from apps.cardano.byron import CURVE, seed
from apps.cardano.byron.address import (
    derive_address_and_node,
    is_safe_output_address,
    validate_full_path,
)
from apps.cardano.layout import confirm_sending, confirm_certificate, confirm_shelley_transaction, progress
from apps.common import cbor
from apps.common.paths import validate_path
from apps.common.seed import remove_ed25519_prefix

# the maximum allowed change address.  this should be large enough for normal
# use and still allow to quickly brute-force the correct bip32 path
MAX_CHANGE_ADDRESS_INDEX = const(1000000)
ACCOUNT_PREFIX_DEPTH = const(2)

KNOWN_PROTOCOL_MAGICS = {764824073: "Mainnet", 1097911063: "Testnet"}


# we consider addresses from the external chain as possible change addresses as well
def is_change(output, inputs):
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
    ctx,
    outputs: list,
    outcoins: list,
    fee: int,
    network_name: str,
    raw_inputs: list,
    raw_outputs: list,
    certificates: list,
) -> bool:
    for index, output in enumerate(outputs):
        if is_change(raw_outputs[index].address_n, raw_inputs):
            continue

        if not await confirm_sending(ctx, outcoins[index], output):
            return False

    for index, certificate in enumerate(certificates):
        if not await confirm_certificate(ctx, certificate):
            return False

    total_amount = sum(outcoins)
    if not await confirm_shelley_transaction(ctx, total_amount, fee, network_name):
        return False

    return True


async def request_transaction(ctx, tx_req: CardanoTxRequest, index: int):
    tx_req.tx_index = index
    return await ctx.call(tx_req, CardanoTxAck)


async def sign_tx(ctx, msg):
    keychain = await seed.get_keychain(ctx)

    try:
        transaction = Transaction(
            msg.inputs, msg.outputs, keychain, msg.protocol_magic, msg.fee, msg.ttl, msg.certificates
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
    if not await show_tx(
        ctx,
        transaction.output_addresses,
        transaction.outgoing_coins,
        transaction.fee,
        transaction.network_name,
        transaction.inputs,
        transaction.outputs,
        transaction.certificates,
    ):
        raise wire.ActionCancelled("Signing cancelled")

    return tx


class Transaction:
    def __init__(
        self,
        inputs: list,
        outputs: list,
        keychain,
        protocol_magic: int,
        fee,
        ttl,
        certificates: list,
    ):
        self.inputs = inputs
        self.outputs = outputs
        self.keychain = keychain
        self.fee = fee
        self.ttl = ttl
        self.certificates = certificates

        self.network_name = KNOWN_PROTOCOL_MAGICS.get(protocol_magic, "Unknown")
        self.protocol_magic = protocol_magic

    def _process_outputs(self):
        change_addresses = []
        change_derivation_paths = []
        output_addresses = []
        outgoing_coins = []
        change_coins = []

        for output in self.outputs:
            if output.address_n:
                address, _ = derive_address_and_node(self.keychain, output.address_n)
                change_addresses.append(address)
                change_derivation_paths.append(output.address_n)
                change_coins.append(output.amount)
            else:
                if output.address is None:
                    raise wire.ProcessError(
                        "Each output must have address or address_n field!"
                    )
                if not is_safe_output_address(output.address):
                    raise wire.ProcessError("Invalid output address!")

                outgoing_coins.append(output.amount)
                output_addresses.append(output.address)

        self.change_addresses = change_addresses
        self.output_addresses = output_addresses
        self.outgoing_coins = outgoing_coins
        self.change_coins = change_coins
        self.change_derivation_paths = change_derivation_paths


    def _build_witness(self, keychain, protocol_magic, tx_aux_hash, address_path):
        _, node = derive_address_and_node(keychain, address_path)
        message = (
            b"\x01" + cbor.encode(protocol_magic) + b"\x58\x20" + tx_aux_hash
        )
        signature = ed25519.sign_ext(
            node.private_key(), node.private_key_ext(), message
        )
        extended_public_key = (
            remove_ed25519_prefix(node.public_key()) + node.chain_code()
        )
        return [extended_public_key, signature]


    def _build_witnesses(self, tx_aux_hash: str):
        witnesses = []
        for input in self.inputs:
            witness = self._build_witness(self.keychain, self.protocol_magic, tx_aux_hash, input.address_n)
            witnesses.append(witness)

        for certificate in self.certificates:
            # todo: add other certificates without witnesses + refactor
            if (certificate.type == "stake_registration"):
                continue

            witness = self._build_witness(self.keychain, self.protocol_magic, tx_aux_hash, certificate.path)
            witnesses.append(witness)

        return {0: witnesses}


    # todo: move?
    def certificate_type_to_type_id(self, certificate_type):
        if certificate_type == 'stake_registration':
            return 0
        if certificate_type == 'stake_deregistration':
            return 1
        if certificate_type == 'stake_delegation':
            return 2
        
        raise ValueError("Unsupported certificate type '%s'" % certificate_type)


    def serialise_tx(self):

        self._process_outputs()

        inputs_cbor = []
        for input in self.inputs:
            inputs_cbor.append([input.prev_hash, input.prev_index])

        # todo: cbor.Set
        inputs_cbor = cbor.Set(inputs_cbor)

        outputs_cbor = []
        for index, address in enumerate(self.output_addresses):
            outputs_cbor.append(
                # todo: bech32?
                [cbor.Raw(base58.decode(address)), self.outgoing_coins[index]]
            )

        for index, address in enumerate(self.change_addresses):
            outputs_cbor.append(
                # todo: bech32?
                [cbor.Raw(base58.decode(address)), self.change_coins[index]]
            )

        outputs_cbor = cbor.IndefiniteLengthArray(outputs_cbor)

        # todo: certificates, withdrawals, update, metadata
        tx_aux_cbor = {0: inputs_cbor, 1: outputs_cbor, 2: self.fee, 3: self.ttl}

        if len(self.certificates) > 0:
            certificates_cbor = []
            for index, certificate in enumerate(self.certificates):
                _, node = derive_address_and_node(self.keychain, certificate.path)
                public_key_hash = hashlib.blake2b(data=node.public_key(), outlen=32).digest()
                # todo: 0 deppends on cert type
                cert_type_id = self.certificate_type_to_type_id(certificate.type)
                certificates_cbor.append([cert_type_id, public_key_hash])

            tx_aux_cbor[4] = certificates_cbor

        tx_hash = hashlib.blake2b(data=cbor.encode(tx_aux_cbor), outlen=32).digest()

        witnesses = self._build_witnesses(tx_hash)
        tx_body = cbor.encode([tx_aux_cbor, witnesses])

        print("tx_body: ", tx_body)
        print("tx_hash:", tx_hash)

        return tx_body, tx_hash
