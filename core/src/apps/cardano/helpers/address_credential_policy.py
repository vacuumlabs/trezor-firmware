from trezor.enums import CardanoAddressType

from .paths import CHAIN_STAKING_KEY, SCHEMA_PAYMENT, SCHEMA_STAKING
from .utils import to_account_path

if False:
    from trezor.messages import CardanoAddressParametersType


ADDRESS_POLICY_SHOW_SPLIT = 0
ADDRESS_POLICY_SHOW_SIMPLE = 1


class CredentialPolicy:
    NONE = 0
    WARN = 1
    WARN_REWARD = 1 << 1 | WARN
    WARN_NO_STAKING = 1 << 2 | WARN
    WARN_MISMATCH = 1 << 3 | WARN
    WARN_UNUSUAL_PATH = 1 << 4 | WARN

    @classmethod
    def check(cls, policy: int, bits_to_check: int) -> int:
        """Checks if `policy` contains all bits of `bits_to_check`."""
        return (policy & bits_to_check) == bits_to_check

    @classmethod
    def maybe_unusual(cls, policy: int, is_unusual: bool) -> int:
        """Optionally adds bits of WARN_UNUSUAL_PATH to the `policy`."""
        return policy | cls.WARN_UNUSUAL_PATH if is_unusual else policy


def get_address_policy(address_parameters: CardanoAddressParametersType) -> int:
    if (
        address_parameters.address_type == CardanoAddressType.BASE
        and SCHEMA_PAYMENT.match(address_parameters.address_n)
        and _do_base_address_credentials_match(
            address_parameters.address_n,
            address_parameters.address_n_staking,
        )
    ):
        return ADDRESS_POLICY_SHOW_SIMPLE

    return ADDRESS_POLICY_SHOW_SPLIT


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
        is_unusual = not SCHEMA_PAYMENT.match(address_parameters.address_n)
        return CredentialPolicy.maybe_unusual(CredentialPolicy.NONE, is_unusual)

    elif address_parameters.address_type in (
        CardanoAddressType.BASE_SCRIPT_KEY,
        CardanoAddressType.BASE_SCRIPT_SCRIPT,
        CardanoAddressType.POINTER_SCRIPT,
        CardanoAddressType.ENTERPRISE_SCRIPT,
    ):
        return CredentialPolicy.WARN

    elif address_parameters.address_type in (
        CardanoAddressType.REWARD,
        CardanoAddressType.REWARD_SCRIPT,
    ):
        return CredentialPolicy.WARN_REWARD

    else:
        raise ValueError("Invalid address type")


def get_stake_credential_policy(
    address_parameters: CardanoAddressParametersType,
) -> int:
    address_type = address_parameters.address_type
    if address_type == CardanoAddressType.BASE:
        is_unusual = (
            address_parameters.address_n_staking != []
            and not SCHEMA_STAKING.match(address_parameters.address_n_staking)
        )
        if address_parameters.staking_key_hash:
            return CredentialPolicy.maybe_unusual(CredentialPolicy.WARN, is_unusual)
        if not _do_base_address_credentials_match(
            address_parameters.address_n,
            address_parameters.address_n_staking,
        ):
            return CredentialPolicy.maybe_unusual(
                CredentialPolicy.WARN_MISMATCH, is_unusual
            )
        return CredentialPolicy.maybe_unusual(CredentialPolicy.NONE, is_unusual)

    elif address_type == CardanoAddressType.BASE_SCRIPT_KEY:
        is_unusual = (
            address_parameters.address_n_staking != []
            and not SCHEMA_STAKING.match(address_parameters.address_n_staking)
        )
        return CredentialPolicy.maybe_unusual(CredentialPolicy.NONE, is_unusual)

    elif address_type in (
        CardanoAddressType.POINTER,
        CardanoAddressType.POINTER_SCRIPT,
    ):
        return CredentialPolicy.WARN

    elif address_type == CardanoAddressType.REWARD:
        is_unusual = not SCHEMA_STAKING.match(address_parameters.address_n_staking)
        return CredentialPolicy.maybe_unusual(CredentialPolicy.NONE, is_unusual)

    elif address_type in (
        CardanoAddressType.BASE_KEY_SCRIPT,
        CardanoAddressType.BASE_SCRIPT_SCRIPT,
        CardanoAddressType.REWARD_SCRIPT,
    ):
        return CredentialPolicy.WARN

    elif address_type in (
        CardanoAddressType.ENTERPRISE,
        CardanoAddressType.ENTERPRISE_SCRIPT,
        CardanoAddressType.BYRON,
    ):
        return CredentialPolicy.WARN_NO_STAKING

    else:
        raise ValueError("Invalid address type")


def _do_base_address_credentials_match(
    address_n: list[int],
    address_n_staking: list[int],
) -> bool:
    return address_n_staking == _path_to_staking_path(address_n)


def _path_to_staking_path(path: list[int]) -> list[int]:
    return to_account_path(path) + [CHAIN_STAKING_KEY, 0]
