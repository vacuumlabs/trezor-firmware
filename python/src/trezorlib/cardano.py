# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

from typing import List

from . import messages, tools
from .tools import expect, session

REQUIRED_FIELDS_TRANSACTION = ("inputs", "outputs", "transactions")
REQUIRED_FIELDS_INPUT = ("path", "prev_hash", "prev_index", "type")


@expect(messages.CardanoAddress, field="address")
def get_address(
    client,
    address_n,
    show_display=False,
    address_type=messages.CardanoAddressType.BASE_ADDRESS,
    network_id=0,
    certificate_pointer=None,
    staking_key_hash=None,
):
    return client.call(
        messages.CardanoGetAddress(
            address_n=address_n,
            show_display=show_display,
            address_type=address_type,
            network_id=network_id,
            certificate_pointer=certificate_pointer,
            staking_key_hash=staking_key_hash,
        )
    )


@expect(messages.CardanoPublicKey)
def get_public_key(client, address_n):
    return client.call(messages.CardanoGetPublicKey(address_n=address_n))


@session
def sign_tx(
    client,
    inputs: List[messages.CardanoTxInputType],
    outputs: List[messages.CardanoTxOutputType],
    transactions: List[bytes],
    protocol_magic,
):
    response = client.call(
        messages.CardanoSignTx(
            inputs=inputs,
            outputs=outputs,
            transactions_count=len(transactions),
            protocol_magic=protocol_magic,
        )
    )

    while isinstance(response, messages.CardanoTxRequest):
        tx_index = response.tx_index

        transaction_data = bytes.fromhex(transactions[tx_index])
        ack_message = messages.CardanoTxAck(transaction=transaction_data)
        response = client.call(ack_message)

    return response


def create_certificate_pointer(
    block_index: int, tx_index: int, certificate_index: int
) -> messages.CardanoCertificatePointerType:
    if block_index is None or tx_index is None or certificate_index is None:
        raise ValueError("Invalid pointer parameters")

    return messages.CardanoCertificatePointerType(
        block_index=block_index, tx_index=tx_index, certificate_index=certificate_index
    )


def create_input(input) -> messages.CardanoTxInputType:
    if not all(input.get(k) is not None for k in REQUIRED_FIELDS_INPUT):
        raise ValueError("The input is missing some fields")

    path = input["path"]

    return messages.CardanoTxInputType(
        address_n=tools.parse_path(path),
        prev_hash=bytes.fromhex(input["prev_hash"]),
        prev_index=input["prev_index"],
        type=input["type"],
    )


def create_output(output) -> messages.CardanoTxOutputType:
    if not output.get("amount") or not (output.get("address") or output.get("path")):
        raise ValueError("The output is missing some fields")

    if output.get("path"):
        path = output["path"]

        return messages.CardanoTxOutputType(
            address_n=tools.parse_path(path), amount=int(output["amount"])
        )

    return messages.CardanoTxOutputType(
        address=output["address"], amount=int(output["amount"])
    )
