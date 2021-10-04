from common import *

from apps.cardano.helpers.address_credential_policy import (
    CredentialPolicy,
    get_payment_credential_policy,
    get_stake_credential_policy,
)
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
        CredentialPolicy.NONE,
        CredentialPolicy.NONE,
    ),
    # base mismatch
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 1 | HARDENED, 2, 0],
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN_MISMATCH,
    ),
    # base payment unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN_MISMATCH,
    ),
    # base staking unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN_UNUSUAL_PATH,
    ),
    # base both unusual and mismatch
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 102 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN_MISMATCH | CredentialPolicy.WARN_UNUSUAL_PATH,
    ),
    # base staking key hash
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            staking_key_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN,
    ),
    # base key script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_KEY_SCRIPT,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            staking_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN,
    ),
    # base key script unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_KEY_SCRIPT,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            staking_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN,
    ),
    # base script key
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_KEY,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN,
        CredentialPolicy.NONE,
    ),
    # base script key unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_KEY,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN,
        CredentialPolicy.WARN_UNUSUAL_PATH,
    ),
    # base script script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BASE_SCRIPT_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            staking_script_hash="2bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.WARN,
        CredentialPolicy.WARN,
    ),
    # pointer
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN,
    ),
    # pointer unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN,
    ),
    # pointer script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.POINTER_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
            certificate_pointer=CERTIFICATE_POINTER,
        ),
        CredentialPolicy.WARN,
        CredentialPolicy.WARN,
    ),
    # enterprise
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN_NO_STAKING,
    ),
    # enterprise unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE,
            address_n=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN_NO_STAKING,
    ),
    # enterprise script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.ENTERPRISE_SCRIPT,
            payment_script_hash="1bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.WARN,
        CredentialPolicy.WARN_NO_STAKING,
    ),
    # reward
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD,
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN_REWARD,
        CredentialPolicy.NONE,
    ),
    # reward unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD,
            address_n_staking=[1852 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 2, 0],
        ),
        CredentialPolicy.WARN_REWARD,
        CredentialPolicy.WARN_UNUSUAL_PATH,
    ),
    # reward script
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.REWARD_SCRIPT,
            staking_script_hash="2bc428e4720732ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff",
        ),
        CredentialPolicy.WARN_REWARD,
        CredentialPolicy.WARN,
    ),
    # byron
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BYRON,
            address_n=[44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
        ),
        CredentialPolicy.NONE,
        CredentialPolicy.WARN_NO_STAKING,
    ),
    # byron unusual
    (
        CardanoAddressParametersType(
            address_type=CardanoAddressType.BYRON,
            address_n=[44 | HARDENED, 1815 | HARDENED, 101 | HARDENED, 0, 0],
        ),
        CredentialPolicy.WARN_UNUSUAL_PATH,
        CredentialPolicy.WARN_NO_STAKING,
    )
]


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoCredentialPolicy(unittest.TestCase):
    def test_get_credential_policies(self):
        for (
            address_parameters,
            expected_payment_policy,
            expected_stake_policy,
        ) in ADDRESS_PARAMETERS_CASES:
            payment_policy = get_payment_credential_policy(address_parameters)
            stake_policy = get_stake_credential_policy(address_parameters)
            self.assertEqual(payment_policy, expected_payment_policy)
            self.assertEqual(stake_policy, expected_stake_policy)


if __name__ == "__main__":
    unittest.main()
