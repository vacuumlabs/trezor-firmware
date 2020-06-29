from micropython import const
from ubinascii import unhexlify

from trezor import log, wire
from trezor.crypto import base58, hashlib
from trezor.crypto.curve import ed25519
from trezor.messages.CardanoSignedTx import CardanoSignedTx

from apps.cardano import CURVE, seed
from apps.cardano.address import derive_address, validate_full_path
from apps.cardano.bootstrap_address import is_safe_output_address
from apps.cardano.layout import confirm_sending, confirm_transaction
from apps.common import cbor
from apps.common.paths import validate_path
from apps.common.seed import remove_ed25519_prefix

if False:
    from typing import List, Tuple
    from trezor import wire
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
) -> None:
    for index, output in enumerate(outputs):
        if raw_outputs[index].address_parameters and is_change(
            raw_outputs[index].address_parameters.address_n, raw_inputs
        ):
            continue

        await confirm_sending(ctx, outcoins[index], output)

    total_amount = sum(outcoins)
    await confirm_transaction(ctx, total_amount, fee, network_name)


@seed.with_keychain
async def sign_tx(
    ctx: wire.Context, msg: CardanoSignTx, keychain: seed.Keychain
) -> CardanoSignedTx:
    try:
        transaction = Transaction(
            msg.inputs, msg.outputs, keychain, msg.protocol_magic, msg.fee, msg.ttl
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
    ) -> None:
        self.inputs = inputs
        self.outputs = outputs
        self.keychain = keychain
        self.fee = fee
        self.ttl = ttl

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

    def _build_input_witnesses(self, tx_aux_hash: bytes) -> List[List[bytes, bytes]]:
        input_witnesses = []
        for input in self.inputs:
            node = self.keychain.derive(input.address_n)
            message = b"\x58\x20" + tx_aux_hash

            signature = ed25519.sign_ext(
                node.private_key(), node.private_key_ext(), message
            )

            public_key = remove_ed25519_prefix(node.public_key())

            input_witnesses.append([public_key, signature])

        # todo: GK - resolve for certificates and byron witnesses

        return input_witnesses

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

        # todo: certificates, withdrawals, metadata
        tx_body = {0: inputs_for_cbor, 1: outputs_for_cbor, 2: self.fee, 3: self.ttl}

        tx_body_cbor = cbor.encode(tx_body)
        tx_hash = hashlib.blake2b(data=tx_body_cbor, outlen=32).digest()

        witnesses = {0: self._build_input_witnesses(tx_hash)}

        tx = cbor.encode([tx_body, witnesses, {}])

        return tx, tx_hash
