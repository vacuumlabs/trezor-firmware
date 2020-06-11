from micropython import const

from trezor import log, wire
from trezor.crypto import base58, hashlib
from trezor.crypto.curve import ed25519
from trezor.messages.CardanoSignedTx import CardanoSignedTx

from apps.cardano import CURVE, seed
from apps.cardano.address import derive_address, validate_full_path
from apps.cardano.bootstrap_address import is_safe_output_address
from apps.cardano.layout import confirm_sending, confirm_transaction, progress
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
) -> None:
    for index, output in enumerate(outputs):
        if is_change(raw_outputs[index].address_n, raw_inputs):
            continue

        await confirm_sending(ctx, outcoins[index], output)

    total_amount = sum(outcoins)
    await confirm_transaction(ctx, total_amount, fee, network_name)


@seed.with_keychain
async def sign_tx(ctx, msg, keychain: seed.Keychain):
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
        "Shelley -- " + transaction.network_name,
        transaction.inputs,
        transaction.outputs,
    )

    return tx


class Transaction:
    def __init__(
        self,
        inputs: list,
        outputs: list,
        keychain,
        protocol_magic: int,
        fee: int,
        ttl: int,
    ):
        self.inputs = inputs
        self.outputs = outputs
        self.keychain = keychain
        self.fee = fee
        self.ttl = ttl
        # attributes have to be always empty in current Cardano
        self.attributes = {}

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

    def _build_witnesses(self, tx_aux_hash: str):
        witnesses = []
        for input in self.inputs:
            _, node = derive_address_and_node(self.keychain, input.address_n)
            message = (
                b"\x01" + cbor.encode(self.protocol_magic) + b"\x58\x20" + tx_aux_hash
            )
            signature = ed25519.sign_ext(
                node.private_key(), node.private_key_ext(), message
            )
            extended_public_key = (
                remove_ed25519_prefix(node.public_key()) + node.chain_code()
            )
            witnesses.append(
                [
                    (input.type or 0),
                    cbor.Tagged(24, cbor.encode([extended_public_key, signature])),
                ]
            )

        return witnesses

    def serialise_tx(self):

        self._process_outputs()

        inputs_cbor = []
        for input in self.inputs:
            inputs_cbor.append(
                [
                    (input.type or 0),
                    cbor.Tagged(24, cbor.encode([input.prev_hash, input.prev_index])),
                ]
            )

        inputs_cbor = cbor.IndefiniteLengthArray(inputs_cbor)

        outputs_cbor = []
        for index, address in enumerate(self.output_addresses):
            outputs_cbor.append(
                [cbor.Raw(base58.decode(address)), self.outgoing_coins[index]]
            )

        for index, address in enumerate(self.change_addresses):
            outputs_cbor.append(
                [cbor.Raw(base58.decode(address)), self.change_coins[index]]
            )

        outputs_cbor = cbor.IndefiniteLengthArray(outputs_cbor)

        tx_aux_cbor = [inputs_cbor, outputs_cbor, self.attributes]
        tx_hash = hashlib.blake2b(data=cbor.encode(tx_aux_cbor), outlen=32).digest()

        witnesses = self._build_witnesses(tx_hash)
        tx_body = cbor.encode([tx_aux_cbor, witnesses])

        return tx_body, tx_hash
