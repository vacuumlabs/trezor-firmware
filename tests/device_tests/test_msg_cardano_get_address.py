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

from trezorlib.cardano import get_address
from trezorlib.messages import CardanoAddressType
from trezorlib.tools import parse_path

from ..common import MNEMONIC12


SHELLEY_TEST_VECTORS_MNEMONIC = (
    "test walk nut penalty hip pave soap entry language right filter choice"
)


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "path,expected_address",
    [
        (
            "m/44'/1815'/0'/0/0",
            "Ae2tdPwUPEZLCq3sFv4wVYxwqjMH2nUzBVt1HFr4v87snYrtYq3d3bq2PUQ",
        ),
        (
            "m/44'/1815'/0'/0/1",
            "Ae2tdPwUPEZEY6pVJoyuNNdLp7VbMB7U7qfebeJ7XGunk5Z2eHarkcN1bHK",
        ),
        (
            "m/44'/1815'/0'/0/2",
            "Ae2tdPwUPEZ3gZD1QeUHvAqadAV59Zid6NP9VCR9BG5LLAja9YtBUgr6ttK",
        ),
    ],
)
@pytest.mark.setup_client(mnemonic=MNEMONIC12)
def test_cardano_get_address(client, path, expected_address):
    # data from https://iancoleman.io/bip39/
    address = get_address(
        client, parse_path(path), address_type=CardanoAddressType.BOOTSTRAP_ADDRESS
    )
    assert address == expected_address


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "path, network_id, expected_address",
    [
        (
            "m/1852'/1815'/0'/0/0",
            0,
            "addr1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqcyl47r",
        ),
        (
            "m/1852'/1815'/0'/0/0",
            3,
            "addr1qw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqzhyupd",
        ),
    ],
)
@pytest.mark.setup_client(mnemonic=SHELLEY_TEST_VECTORS_MNEMONIC)
def test_cardano_get_base_address(client, path, network_id, expected_address):
    # data form shelley test vectors
    address = get_address(
        client,
        parse_path(path),
        network_id=network_id,
        address_type=CardanoAddressType.BASE_ADDRESS,
    )
    assert address == expected_address


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "path, network_id, expected_address",
    [
        (
            "m/1852'/1815'/0'/0/0",
            0,
            "addr1vz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6g8jlq",
        ),
        (
            "m/1852'/1815'/0'/0/0",
            3,
            "addr1vw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6h7glf",
        ),
    ],
)
@pytest.mark.setup_client(mnemonic=SHELLEY_TEST_VECTORS_MNEMONIC)
def test_cardano_get_enterprise_address(client, path, network_id, expected_address):
    # data form shelley test vectors
    address = get_address(
        client,
        parse_path(path),
        network_id=network_id,
        address_type=CardanoAddressType.ENTERPRISE_ADDRESS,
    )
    assert address == expected_address


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "path, network_id, block_index, tx_index, certificate_index, expected_address",
    [
        (
            "m/1852'/1815'/0'/0/0",
            0,
            1,
            2,
            3,
            "addr1gz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerspqgpslhplej",
        ),
        (
            "m/1852'/1815'/0'/0/0",
            3,
            24157,
            177,
            42,
            "addr1gw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5ph3wczvf2x4v58t",
        ),
    ],
)
@pytest.mark.setup_client(mnemonic=SHELLEY_TEST_VECTORS_MNEMONIC)
def test_cardano_get_pointer_address(
    client, path, network_id, block_index, tx_index, certificate_index, expected_address
):
    # data form shelley test vectors
    address = get_address(
        client,
        parse_path(path),
        network_id=network_id,
        block_index=block_index,
        tx_index=tx_index,
        certificate_index=certificate_index,
        address_type=CardanoAddressType.POINTER_ADDRESS,
    )
    assert address == expected_address
