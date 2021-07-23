from trezor.enums import CardanoAddressType

from ..address import get_public_key_hash
from .paths import CHAIN_STAKING_KEY, SCHEMA_PAYMENT, SCHEMA_STAKING
from .utils import to_account_path

if False:
    from trezor.messages import CardanoAddressParametersType
    from ..seed import Keychain


CREDENTIAL_POLICY_SHOW = 0
CREDENTIAL_POLICY_SHOW_KEY_PATH = 1 << 1
CREDENTIAL_POLICY_SHOW_CHANGE_OUTPUT = 1 << 2
CREDENTIAL_POLICY_SHOW_ADDRESS = 1 << 3
CREDENTIAL_POLICY_WARN_SCRIPT = 1 << 4
CREDENTIAL_POLICY_WARN_POINTER = 1 << 5
CREDENTIAL_POLICY_WARN_REWARD_ADDRESS = 1 << 6
CREDENTIAL_POLICY_WARN_NO_STAKING = 1 << 7
CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL = 1 << 8
CREDENTIAL_POLICY_WARN_MISMATCH = 1 << 9

CREDENTIAL_POLICIES_WARN = (
    CREDENTIAL_POLICY_WARN_SCRIPT,
    CREDENTIAL_POLICY_WARN_POINTER,
    CREDENTIAL_POLICY_WARN_REWARD_ADDRESS,
    CREDENTIAL_POLICY_WARN_NO_STAKING,
    CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL,
    CREDENTIAL_POLICY_WARN_MISMATCH,
)

ADDRESS_POLICY_SHOW_SPLIT = 0
ADDRESS_POLICY_SHOW_SIMPLE = 1


def get_address_policy(
    keychain: Keychain, address_parameters: CardanoAddressParametersType
) -> int:
    if (
        address_parameters.address_type == CardanoAddressType.BASE
        and SCHEMA_PAYMENT.match(address_parameters.address_n)
        and _do_base_address_credentials_match(
            keychain,
            address_parameters.address_n,
            address_parameters.address_n_staking,
            address_parameters.staking_key_hash,
        )
    ):
        return ADDRESS_POLICY_SHOW_SIMPLE

    return ADDRESS_POLICY_SHOW_SPLIT


def get_change_output_payment_credential_policy(
    address_parameters: CardanoAddressParametersType,
) -> int:
    credential_policy = get_payment_credential_policy(address_parameters)
    return _policy_to_change_output_policy(credential_policy)


def get_change_output_stake_credential_policy(
    keychain: Keychain, address_parameters: CardanoAddressParametersType
) -> int:
    credential_policy = get_stake_credential_policy(keychain, address_parameters)
    return _policy_to_change_output_policy(credential_policy)


def get_payment_credential_policy(
    address_parameters: CardanoAddressParametersType,
) -> int:
    if address_parameters.address_type in (
        CardanoAddressType.BASE,
        CardanoAddressType.BASE_KEY_SCRIPT,
        CardanoAddressType.POINTER,
        CardanoAddressType.ENTERPRISE,
        CardanoAddressType.BYRON,
    ):
        if not SCHEMA_PAYMENT.match(address_parameters.address_n):
            return CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL

        return CREDENTIAL_POLICY_SHOW_KEY_PATH

    elif address_parameters.address_type in (
        CardanoAddressType.BASE_SCRIPT_KEY,
        CardanoAddressType.BASE_SCRIPT_SCRIPT,
        CardanoAddressType.POINTER_SCRIPT,
        CardanoAddressType.ENTERPRISE_SCRIPT,
    ):
        return CREDENTIAL_POLICY_WARN_SCRIPT

    elif address_parameters.address_type in (
        CardanoAddressType.REWARD,
        CardanoAddressType.REWARD_SCRIPT,
    ):
        return CREDENTIAL_POLICY_WARN_REWARD_ADDRESS

    else:
        raise ValueError("Invalid address type")


def get_stake_credential_policy(
    keychain: Keychain, address_parameters: CardanoAddressParametersType
) -> int:
    address_type = address_parameters.address_type
    if address_type == CardanoAddressType.BASE:
        is_unusual = address_parameters.address_n_staking and not SCHEMA_STAKING.match(
            address_parameters.address_n_staking
        )

        if not _do_base_address_credentials_match(
            keychain,
            address_parameters.address_n,
            address_parameters.address_n_staking,
            address_parameters.staking_key_hash,
        ):
            return (
                CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL | CREDENTIAL_POLICY_WARN_MISMATCH
                if is_unusual
                else CREDENTIAL_POLICY_WARN_MISMATCH
            )

        return (
            CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL
            if is_unusual
            else CREDENTIAL_POLICY_SHOW
        )

    elif address_type == CardanoAddressType.BASE_SCRIPT_KEY:
        is_unusual = address_parameters.address_n_staking and not SCHEMA_STAKING.match(
            address_parameters.address_n_staking
        )
        return (
            CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL | CREDENTIAL_POLICY_WARN_MISMATCH
            if is_unusual
            else CREDENTIAL_POLICY_WARN_MISMATCH
        )

    elif address_type in (
        CardanoAddressType.POINTER,
        CardanoAddressType.POINTER_SCRIPT,
    ):
        return CREDENTIAL_POLICY_WARN_POINTER

    elif address_type == CardanoAddressType.REWARD:
        return CREDENTIAL_POLICY_SHOW_KEY_PATH

    elif address_type in (
        CardanoAddressType.BASE_KEY_SCRIPT,
        CardanoAddressType.BASE_SCRIPT_SCRIPT,
        CardanoAddressType.REWARD_SCRIPT,
    ):
        return CREDENTIAL_POLICY_WARN_SCRIPT

    elif address_type in (
        CardanoAddressType.ENTERPRISE,
        CardanoAddressType.ENTERPRISE_SCRIPT,
        CardanoAddressType.BYRON,
    ):
        return CREDENTIAL_POLICY_WARN_NO_STAKING

    else:
        raise ValueError("Invalid address type")


def _do_base_address_credentials_match(
    keychain: Keychain,
    address_n: list[int],
    address_n_staking: list[int],
    staking_key_hash: bytes | None,
) -> bool:
    assert address_n_staking or staking_key_hash is not None

    spending_account_staking_path = _path_to_staking_path(address_n)
    if address_n_staking:
        if address_n_staking != spending_account_staking_path:
            return False
    else:
        spending_account_staking_key_hash = get_public_key_hash(
            keychain, spending_account_staking_path
        )
        if staking_key_hash != spending_account_staking_key_hash:
            return False
    return True


def _path_to_staking_path(path: list[int]) -> list[int]:
    return to_account_path(path) + [CHAIN_STAKING_KEY, 0]


def _policy_to_change_output_policy(
    credential_policy: int,
) -> int:
    """
    Updates the policy to a tx change output policy. As a result, different text will be displayed to the user.
    """
    return credential_policy | CREDENTIAL_POLICY_SHOW_CHANGE_OUTPUT
