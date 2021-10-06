from common import *

from apps.cardano.helpers.credential_params import CredentialParams
from apps.common.paths import HARDENED
from trezor.enums import CardanoAddressType
from trezor.messages import CardanoAddressParametersType, CardanoBlockchainPointerType


CERTIFICATE_POINTER = CardanoBlockchainPointerType(
    block_index=24157,
    tx_index=177,
    certificate_index=42,
)

ADDRESS_PARAMETERS_CASES = [
    # base
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        [False, False, False, False, False],
        [False, False, False, False, False],
    ),
    # base mismatch
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 1 | HARDENED, 2, 0],
        ),
        [False, False, False, False, False],
        [False, False, True, False, False],
    ),
    # base payment unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        [False, False, False, True, False],
        [False, False, True, False, False],
    ),
    # base staking unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        [False, False, False, True, False],
        [False, False, False, True, False],
    ),
    # base both unusual and mismatch
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 102 | HARDENED, 2, 0],
        ),
        [False, False, False, True, False],
        [False, False, True, True, False],
    ),
    # base staking key hash
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            staking_key_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [False, False, False, False, False],
        [False, False, False, False, True],
    ),
    # base key script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_KEY_SCRIPT,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            staking_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [False, False, False, False, False],
        [False, False, False, False, True],
    ),
    # base key script unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_KEY_SCRIPT,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            staking_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [False, False, False, True, False],
        [False, False, False, False, True],
    ),
    # base script key
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_KEY,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        [False, False, False, False, True],
        [False, False, False, False, False],
    ),
    # base script key unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_KEY,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        [False, False, False, False, True],
        [False, False, False, True, False],
    ),
    # base script script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            staking_script_hash="2bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [False, False, False, False, True],
        [False, False, False, False, True],
    ),
    # pointer
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        [False, False, False, False, False],
        [False, False, False, False, True],
    ),
    # pointer unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        [False, False, False, True, False],
        [False, False, False, False, True],
    ),
    # pointer script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        [False, False, False, False, True],
        [False, False, False, False, True],
    ),
    # enterprise
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
        ),
        [False, False, False, False, False],
        [False, True, False, False, False],
    ),
    # enterprise unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
        ),
        [False, False, False, True, False],
        [False, True, False, False, False],
    ),
    # enterprise script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [False, False, False, False, True],
        [False, True, False, False, False],
    ),
    # reward
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD,
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        [True, False, False, False, False],
        [False, False, False, False, False],
    ),
    # reward unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD,
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        [True, False, False, False, False],
        [False, False, False, True, False],
    ),
    # reward script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD_SCRIPT,
            staking_script_hash="2bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        [True, False, False, False, False],
        [False, False, False, False, True],
    ),
    # byron
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BYRON,
            address_n=[44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
        ),
        [False, False, False, False, False],
        [False, True, False, False, False],
    ),
    # byron unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BYRON,
            address_n=[44 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
        ),
        [False, False, False, True, False],
        [False, True, False, False, False],
    )
]


def _get_flags(credential_params: CredentialParams) -> list[bool]:
    return [
        credential_params.is_reward,
        credential_params.is_no_staking,
        credential_params.is_mismatch,
        credential_params.is_unusual_path,
        credential_params.is_other_warning,
    ]


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoCredentialParams(unittest.TestCase):
    def test_credential_params_flags(self):
        for (
            address_parameters,
            expected_payment_flags,
            expected_stake_flags,
        ) in ADDRESS_PARAMETERS_CASES:
            payment_credential = CredentialParams.payment_params(address_parameters)
            stake_credential = CredentialParams.stake_params(address_parameters)
            self.assertEqual(_get_flags(payment_credential), expected_payment_flags)
            self.assertEqual(_get_flags(stake_credential), expected_stake_flags)


if __name__ == "__main__":
    unittest.main()
