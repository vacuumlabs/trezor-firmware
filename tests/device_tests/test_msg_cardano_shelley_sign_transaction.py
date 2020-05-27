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

import pytest

from trezorlib import cardano, messages
from trezorlib.exceptions import TrezorFailure

# input flow sequence constants
SWIPE="SWIPE"
YES="YES"
YIELD="YIELD"

PROTOCOL_MAGICS = {"mainnet": 764824073, "testnet": 1097911063}

SAMPLE_INPUTS = [
    {
        "input": {
            "path": "m/44'/1815'/0'/0/1",
            "prev_hash": "1af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc",
            "prev_index": 0,
            "type": 0,
        },
    }
]

SAMPLE_CERTIFICATES = {
    "stake_registration": {
        "type": "stake_registration",
        "path": "m/44'/1815'/0'/2/1",
    },
    "stake_deregistration": {
        "type": "stake_deregistration",
        "path": "m/44'/1815'/0'/2/1"
    },
    "stake_delegation": {
        "type": "stake_delegation",
        "path": "m/44'/1815'/0'/2/1",
        "pool": "f61c42cbf7c8c53af3f520508212ad3e72f674f957fe23ff0acb49733c37b8f6",
    },
}

VALID_VECTORS = [
    # Mainnet transaction with change and stake registration certificate
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # inputs
        [SAMPLE_INPUTS[0]["input"]],
        # outputs
        [
            {
                "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
                "amount": "3003112",
            },
            {"path": "m/44'/1815'/0'/0/1", "amount": "7120787"},
        ],
        # fee
        10000,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_registration"],
        ],
        # tx hash
        "5376267f4d76d1ba23c118b495af067f9bfa4035bd00d03bf00bac37fbb76235",
        # tx body
        "82a500d90102818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00019f8282d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e88282d818582183581cda4da43db3fca93695e71dab839e72271204d28b9d964d306b8800a8a0001a7a6916a51a006ca793ff02192710030a048182005820429c470feae566b939574e41630eadbb291e71abcbaa7a40abcd252627450659a1008182584089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea26308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63558404393c37097e311dcd69d97253da1f4c492c86ee063494d2728675fa2b77ec9b0462970c21b47d8f90c9139df017f2e76a699df6aadb9b9229f04b8540ca0de0d",
        # input flow
        [[SWIPE,YES],[YES],[SWIPE,YES]],
    ),
    # Mainnet transaction with change and stake deregistration certificate
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # inputs
        [SAMPLE_INPUTS[0]["input"]],
        # outputs
        [
            {
                "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
                "amount": "3003112",
            },
            {"path": "m/44'/1815'/0'/0/1", "amount": "7120787"},
        ],
        # fee
        10000,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_deregistration"],
        ],
        # tx hash
        "7501eb363f697dea1bce633039a0dcedf5311f393d3e5acb8be96d0963f4066e",
        # tx body
        "82a500d90102818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00019f8282d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e88282d818582183581cda4da43db3fca93695e71dab839e72271204d28b9d964d306b8800a8a0001a7a6916a51a006ca793ff02192710030a048182015820429c470feae566b939574e41630eadbb291e71abcbaa7a40abcd252627450659a1008282584089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea26308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63558402818da73717cda4e5c0dda7aa54af27f47a8e9598b6d8d5c3008133f9d7cf80872d5cbf7c37563ac1a59d7e73c5c911619e51916b7f56fcd04007946c2969e08825840f5f68c614c44b483740dae7777b12d48658c91d4768f374b0c5972b24d16d25fb5225dd8e331934bd20d98919ae3bea76018662902d82f4d4553f301298a200558401f0227be41c35c324b6dfaab77b93a9eb4388a496ca9d12437a0a239aa1e74806560856bce0198232f38d450b2a1a3bf2e41617e0b730d4167fd04621ea51c09",
        # input flow
        [[SWIPE,YES],[YES],[SWIPE,YES]],
    ),
    # Mainnet transaction with change and stake delegation certificate
    (
        # protocol magic (mainnet)
        PROTOCOL_MAGICS["mainnet"],
        # inputs
        [SAMPLE_INPUTS[0]["input"]],
        # outputs
        [
            {
                "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
                "amount": "3003112",
            },
            {"path": "m/44'/1815'/0'/0/1", "amount": "7120787"},
        ],
        # fee
        10000,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_delegation"],
        ],
        # tx hash
        "626256870c0a56939b285e436fdfe9eda735d604c1dcc122201b4ecac99749bd",
        # tx body
        "82a500d90102818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00019f8282d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e88282d818582183581cda4da43db3fca93695e71dab839e72271204d28b9d964d306b8800a8a0001a7a6916a51a006ca793ff02192710030a048182025820429c470feae566b939574e41630eadbb291e71abcbaa7a40abcd252627450659a1008282584089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea26308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a6355840d2bfd1801318cbe95e94427e55070e52a21d4ca17171856dcfa461fd14faa7767ee20301d056f5a2001f78071e291086866a20cfa5523b865165a04c1bd98706825840f5f68c614c44b483740dae7777b12d48658c91d4768f374b0c5972b24d16d25fb5225dd8e331934bd20d98919ae3bea76018662902d82f4d4553f301298a200558400d15daacb4e818bf231df917f1614805ebda9b886cc0f7f9f88cd34fc1cac7b9c54f60d16a15fb2f2c39a665334e76d6c86e81ce048deb41bb9d867975263307",
        # input flow
        [[SWIPE,YES],[SWIPE,YES],[SWIPE,YES]],
    ),
    # Mainnet transaction with change and stake registration and stake delegation certificates
    (
        # protocol magic (mainnet)
        PROTOCOL_MAGICS["mainnet"],
        # inputs
        [SAMPLE_INPUTS[0]["input"]],
        # outputs
        [
            {
                "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
                "amount": "3003112",
            },
            {"path": "m/44'/1815'/0'/0/1", "amount": "7120787"},
        ],
        # fee
        10000,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_registration"],
            SAMPLE_CERTIFICATES["stake_delegation"],
        ],
        # tx hash
        "cd9d2747a137af409b63cbb2803395545300caba8ed319859acaf949b579c3e1",
        # tx body
        "82a500d90102818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00019f8282d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e88282d818582183581cda4da43db3fca93695e71dab839e72271204d28b9d964d306b8800a8a0001a7a6916a51a006ca793ff02192710030a048282005820429c470feae566b939574e41630eadbb291e71abcbaa7a40abcd25262745065982025820429c470feae566b939574e41630eadbb291e71abcbaa7a40abcd252627450659a1008282584089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea26308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a635584041122457992a7270af7dbac0db7526a3ac900a3ae239fc42fbe40c06350c83fbc8b6c15a891af84e87051e678b09868a22bcd1170cc56b2cd4df5510685a8808825840f5f68c614c44b483740dae7777b12d48658c91d4768f374b0c5972b24d16d25fb5225dd8e331934bd20d98919ae3bea76018662902d82f4d4553f301298a20055840301764862173b8d03cbd8230876bb0414eb76a01b9a07084ff55a86989971c3897a8d4a2af2095ba53c2671c9b6960799666335ed459bcbd6ceabccdb976c309",
        # input flow
        [[SWIPE,YES],[YES],[SWIPE,YES],[SWIPE,YES]],
    ),
]

# todo: invalid vectors


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "protocol_magic,inputs,outputs,fee,ttl,certificates,tx_hash,tx_body,input_flow_sequence", VALID_VECTORS
)
def test_cardano_shelley_sign_tx(
    client, protocol_magic, inputs, outputs, fee, ttl, certificates, tx_hash, tx_body, input_flow_sequence
):
    inputs = [cardano.create_input(i) for i in inputs]
    outputs = [cardano.create_output(o) for o in outputs]
    certificates = [cardano.create_certificate(c) for c in certificates]

    expected_responses = []
    # todo: refactor?
    for i in range(len(input_flow_sequence)):
        expected_responses.append(messages.ButtonRequest(code=messages.ButtonRequestType.Other))

    expected_responses.append(messages.CardanoSignedTx())

    # todo: refactor?
    def input_flow():
        for sub_sequence in input_flow_sequence:
            yield
            for step in sub_sequence:
                if step == SWIPE:
                    client.debug.swipe_up()
                elif step == YES:
                    client.debug.press_yes()

    with client:
        client.set_expected_responses(expected_responses)
        client.set_input_flow(input_flow)
        response = cardano.sign_tx(
            client, inputs, outputs, fee, ttl, certificates, protocol_magic
        )

        assert response.tx_hash.hex() == tx_hash
        assert response.tx_body.hex() == tx_body
