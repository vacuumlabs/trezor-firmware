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

NETWORK_IDS = {"mainnet": 0}

SHELLEY_TEST_VECTORS_MNEMONIC = (
    "test walk nut penalty hip pave soap entry language right filter choice"
)

class InputAction:
    """
    Test cases don't use the same input flows. These constants are used to define
    the expected input flows for each test case. Corresponding input actions
    are then executed on the device to simulate user inputs.
    """
    SWIPE = 0
    YES = 1

SAMPLE_INPUTS = {
    "simple_input": {
        "path": "m/1852'/1815'/0'/0/0",
        "prev_hash": "3b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b7",
        "prev_index": 0,
        # todo: GK - type can be removed?
        "type": 0,
    },
}

SAMPLE_OUTPUTS = {
    "simple_output": {
        "address": "61a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa4",
        "amount": "1",
    },
    "simple_change_output": {
        "addressType": 0,
        "path": "m/1852'/1815'/0'/0/0",
        "amount": "7120787",
    },
    "staking_key_hash_output": {
        "addressType": 0,
        "path": "m/1852'/1815'/0'/0/0",
        "stakingKeyHash": "122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277",
        "amount": "7120787",
    },
    "pointer_address_output": {
        "addressType": 1,
        "path": "m/1852'/1815'/0'/0/0",
        "pointer": {"block_index": 1, "tx_index": 2, "certificate_index": 3},
        "amount": "7120787",
    },
}

SAMPLE_CERTIFICATES = {
    "stake_registration": {
        "type": 17,
        "path": "m/1852'/1815'/0'/2/0",
    },
    "stake_deregistration": {
        "type": 34,
        "path": "m/1852'/1815'/0'/2/0",
    },
    "stake_delegation": {
        "type": 51,
        "path": "m/1852'/1815'/0'/2/0",
        "pool": "f61c42cbf7c8c53af3f520508212ad3e72f674f957fe23ff0acb49733c37b8f6",
    },
}

# todo: GK - add tests with enterprise address
# todo: GK - add tests with bootstrap address

# data generated with code under test
VALID_VECTORS = [
    # simple transaction without change outputs
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "2131a3730ffd7ac43ce676df96d535c3d34cb37c1f26902a8f73db39bd1f4ff6",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa40102182a030aa1008182582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d584045ac6072629070608b3d59116f0e13dec284b67c3e5efe5c6e08b8861b0c66cd114548fb62786289426bd9129b9f45cab82a0d750163bae8f0eb786f0a9eb70ba0",
    ),
    # simple transaction with base address change output
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"], SAMPLE_OUTPUTS["simple_change_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "520b8c28f7be5f977d930b6cbb191a29945fb8af048220f0136eeb5a145288ed",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa401825839009493315cd92eb5d8c4304e67b7e16ae36d61d34502694657811a2c8e32c728d3861e164cab28cb8f006448139c8f1740ffb8e7aa9e5232dc1a006ca79302182a030aa1008182582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d5840ff94b26ae63c067fa23c76f543e22f8eb23c9ff969d7f5136e5da5ac41b03f4b3c8ef0e56ecba9e1488bea046ea18ace0ad425205304d2f38aca67676fd2cc05a0",
    ),
    # simple transaction with base address change output with staking key hash
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"], SAMPLE_OUTPUTS["staking_key_hash_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "b6e3c0dc93e2b098acf3803ab1249c72145ae6d13a45dcab211567771cac2f23",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa401825839009493315cd92eb5d8c4304e67b7e16ae36d61d34502694657811a2c8e122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b42771a006ca79302182a030aa1008182582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d58408de1c8576b63bd53b8e4c992ebf907a0c80bc62cb4dc270fcd00c4ba2f25c96cca95d946885a74e9ff3bda73cab3648c81ed0e971d18905966373df00066aa02a0",
    ),
    # simple transaction with pointer address change output
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"], SAMPLE_OUTPUTS["pointer_address_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "02d5a72fe0278aaa4441dadd883b323e7d82e3389022b9f901c2aafc6e187f7d",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa401825820409493315cd92eb5d8c4304e67b7e16ae36d61d34502694657811a2c8e0102031a006ca79302182a030aa1008182582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d584008d399a6bb1505580d354b2e406c805a48e6854dbfdfb7c9c2778478df0aa1fc8a63eac0fed5fa10db2acb7a7b1da8786a80285f605588442084ca5d5b6d5803a0",
    ),
    # transaction with stake registration certificate
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["stake_registration"]],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "61caeefb2d32d34edd5caa9fdf374331fa764e756ebe9b205193c1bd1bf20a00",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa40102182a030a0481820082005820fcb95695ce37daf2daa2f961d02e05fee8a02be02b499608ea451aed76084e47a1008182582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d5840891c7f3512d935c052879472a2a6e3110d10541be67ad65ce82520525af112be9bae87c4d9a76e34aa6081ebc1f2c3cfa506ca1c01229192176eb891e4950500a0",
    ),
    # transaction with stake registration and stake delegation certificates
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_registration"],
            SAMPLE_CERTIFICATES["stake_delegation"],
        ],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.YES], [InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "61dc133b3d7c4ebc3636bcd3ee1799bc641f2082ad16ee76b4d81007c4826391",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa40102182a030a0482820082005820fcb95695ce37daf2daa2f961d02e05fee8a02be02b499608ea451aed76084e47820282005820fcb95695ce37daf2daa2f961d02e05fee8a02be02b499608ea451aed76084e47a1008282582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d58404648ec125ccea0aa53324592e6595d0820036c171d4c804866b9ff3eba0e75955ea6ac833213eb87825d5ae4b48bdc1dfdc61a192bc932623aea507c2d4e040f8258202c041c9c6a676ac54d25e2fdce44c56581e316ae43adc4c7bf17f23214d8d89258405c4e9d8f28755dd0c9b1957ba9e750fd577337659b868648f2eb2b2d0a6bdc77cb6bddca458392bc4de86b6cfc29d6e51640d94bb8e3306061981ad77532b207a0",
    ),
    # transaction with stake deregistration
    (
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["simple_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["stake_deregistration"]],
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "bda54c36b06db3f52853b6f700a87a4a3de1b5697e1bf4038538fa03cc3cd442",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182582161a6274badf4c9ca583df893a73139625ff4dc73aaa3082e67d6d5d08e0ce3daa40102182a030a0481820182005820fcb95695ce37daf2daa2f961d02e05fee8a02be02b499608ea451aed76084e47a1008282582073fea80d424276ad0978d4fe5310e8bc2d485f5f6bb3bf87612989f112ad5a7d58408b2430cb72d59f7a64f29d3465845ede8377910e88f209fd004c91371018dbb2863babc7a9b62cca09525eb10effce0102dfb35655a85f29fd5b1c92e6af7f038258202c041c9c6a676ac54d25e2fdce44c56581e316ae43adc4c7bf17f23214d8d8925840f4623d7f81ef01304cd12289557158ceaae9c1e70e8f3d850f6a3fed715c3705c4cdd74ff49cb99a7d1c84845e0b842b802919589b6763d9219ba433776c3a00a0",
    ),
]

# todo: GK - add invalid tests


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "protocol_magic,inputs,outputs,fee,ttl,certificates,input_flow_sequences,tx_hash,tx_body",
    VALID_VECTORS,
)
@pytest.mark.setup_client(mnemonic=SHELLEY_TEST_VECTORS_MNEMONIC)
def test_cardano_sign_tx(
    client,
    protocol_magic,
    inputs,
    outputs,
    fee,
    ttl,
    certificates,
    input_flow_sequences,
    tx_hash,
    tx_body,
):
    inputs = [cardano.create_input(i) for i in inputs]
    outputs = [cardano.create_output(o) for o in outputs]
    certificates = [cardano.create_certificate(c) for c in certificates]

    expected_responses = [
        messages.ButtonRequest(code=messages.ButtonRequestType.Other)
        for i in range(len(input_flow_sequences))
    ]
    expected_responses.append(messages.CardanoSignedTx())

    def input_flow():
        for sequence in input_flow_sequences:
            yield
            for action in sequence:
                if action == InputAction.SWIPE:
                    client.debug.swipe_up()
                elif action == InputAction.YES:
                    client.debug.press_yes()
                else:
                    raise ValueError("Invalid input action")

    with client:
        client.set_expected_responses(expected_responses)
        client.set_input_flow(input_flow)
        response = cardano.sign_tx(
            client, inputs, outputs, fee, ttl, certificates, protocol_magic
        )
        assert response.tx_hash.hex() == tx_hash
        assert response.tx_body.hex() == tx_body
