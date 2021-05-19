from trezor.crypto import base58, hashlib
from trezor.messages import CardanoAddressType

from .byron_address import derive_byron_address, validate_byron_address
from .helpers import (
    ADDRESS_KEY_HASH_SIZE,
    INVALID_ADDRESS,
    INVALID_ADDRESS_PARAMETERS,
    NETWORK_MISMATCH,
    bech32,
    network_ids,
)
from .helpers.paths import SCHEMA_STAKING_ANY_ACCOUNT
from .helpers.utils import derive_public_key, variable_length_encode
from .script import get_script_hash, validate_script
from .seed import is_byron_path, is_shelley_path

if False:
    from trezor.messages.CardanoBlockchainPointerType import (
        CardanoBlockchainPointerType,
    )
    from trezor.messages.CardanoAddressParametersType import (
        CardanoAddressParametersType,
        EnumTypeCardanoAddressType,
    )
    from . import seed

ADDRESS_TYPES_SHELLEY = (
    CardanoAddressType.BASE,
    CardanoAddressType.BASE_SCRIPT_KEY,
    CardanoAddressType.BASE_KEY_SCRIPT,
    CardanoAddressType.BASE_SCRIPT_SCRIPT,
    CardanoAddressType.POINTER,
    CardanoAddressType.POINTER_SCRIPT,
    CardanoAddressType.ENTERPRISE,
    CardanoAddressType.ENTERPRISE_SCRIPT,
    CardanoAddressType.REWARD,
    CardanoAddressType.REWARD_SCRIPT,
)
MIN_ADDRESS_BYTES_LENGTH = 29
MAX_ADDRESS_BYTES_LENGTH = 65


# TODO GK unit tests
# TODO GK refactor
def validate_address_parameters(parameters: CardanoAddressParametersType) -> None:
    _validate_address_parameters_structure(parameters)

    if parameters.address_type == CardanoAddressType.BYRON:
        if not is_byron_path(parameters.address_n):
            raise INVALID_ADDRESS_PARAMETERS

    elif parameters.address_type in ADDRESS_TYPES_SHELLEY:
        if parameters.address_type == CardanoAddressType.BASE:
            if not is_shelley_path(parameters.address_n):
                raise INVALID_ADDRESS_PARAMETERS
            _validate_base_address_staking_info(
                parameters.address_n_staking, parameters.staking_key_hash
            )

        elif parameters.address_n == CardanoAddressType.BASE_SCRIPT_KEY:
            _validate_base_address_staking_info(
                parameters.address_n_staking, parameters.staking_key_hash
            )
            validate_script(parameters.script_payment)

        elif parameters.address_n == CardanoAddressType.BASE_KEY_SCRIPT:
            validate_script(parameters.script_staking)

        elif parameters.address_n == CardanoAddressType.BASE_SCRIPT_SCRIPT:
            validate_script(parameters.script_payment)
            validate_script(parameters.script_staking)

        elif parameters.address_type == CardanoAddressType.POINTER:
            if not is_shelley_path(parameters.address_n):
                raise INVALID_ADDRESS_PARAMETERS
            if parameters.certificate_pointer is None:
                raise INVALID_ADDRESS_PARAMETERS

        elif parameters.address_n == CardanoAddressType.POINTER_SCRIPT:
            if parameters.certificate_pointer is None:
                raise INVALID_ADDRESS_PARAMETERS
            validate_script(parameters.script_payment)

        elif parameters.address_type == CardanoAddressType.ENTERPRISE:
            if not is_shelley_path(parameters.address_n):
                raise INVALID_ADDRESS_PARAMETERS

        elif parameters.address_type == CardanoAddressType.ENTERPRISE_SCRIPT:
            validate_script(parameters.script_payment)

        elif parameters.address_type == CardanoAddressType.REWARD:
            if not is_shelley_path(parameters.address_n):
                raise INVALID_ADDRESS_PARAMETERS
            if not SCHEMA_STAKING_ANY_ACCOUNT.match(parameters.address_n):
                raise INVALID_ADDRESS_PARAMETERS

        elif parameters.address_type == CardanoAddressType.REWARD_SCRIPT:
            # TODO GK staking or payment script?
            validate_script(parameters.script_staking)
    else:
        raise INVALID_ADDRESS_PARAMETERS


# TODO GK can perhaps be rewritten in the form of a dict
def _validate_address_parameters_structure(
    parameters: CardanoAddressParametersType,
) -> None:
    address_n = parameters.address_n
    address_n_staking = parameters.address_n_staking
    staking_key_hash = parameters.staking_key_hash
    certificate_pointer = parameters.certificate_pointer
    script_payment = parameters.script_payment
    script_staking = parameters.script_staking

    fields_to_be_empty = {
        CardanoAddressType.BASE: [certificate_pointer, script_payment, script_staking],
        CardanoAddressType.BASE_KEY_SCRIPT: [
            address_n_staking,
            certificate_pointer,
            script_payment,
        ],
        CardanoAddressType.BASE_SCRIPT_KEY: [
            address_n,
            certificate_pointer,
            script_staking,
        ],
        CardanoAddressType.BASE_SCRIPT_SCRIPT: [
            address_n,
            address_n_staking,
            certificate_pointer,
        ],
        CardanoAddressType.POINTER: [
            address_n_staking,
            staking_key_hash,
            script_payment,
            script_staking,
        ],
        CardanoAddressType.POINTER_SCRIPT: [
            address_n,
            address_n_staking,
            staking_key_hash,
            script_staking,
        ],
        CardanoAddressType.ENTERPRISE: [
            address_n_staking,
            staking_key_hash,
            certificate_pointer,
            script_payment,
            script_staking,
        ],
        CardanoAddressType.ENTERPRISE_SCRIPT: [
            address_n,
            address_n_staking,
            staking_key_hash,
            certificate_pointer,
            script_staking,
        ],
        CardanoAddressType.BYRON: [
            address_n_staking,
            staking_key_hash,
            certificate_pointer,
            script_payment,
            script_staking,
        ],
        CardanoAddressType.REWARD: [
            address_n_staking,
            staking_key_hash,
            certificate_pointer,
            script_payment,
            script_staking,
        ],
        CardanoAddressType.REWARD_SCRIPT: [
            address_n,
            address_n_staking,
            staking_key_hash,
            certificate_pointer,
            # TODO GK which script? rename scripts to script and script_staking?
            script_payment,
        ],
    }

    if any(fields_to_be_empty[parameters.address_type]):
        raise INVALID_ADDRESS_PARAMETERS


def _validate_base_address_staking_info(
    staking_path: list[int],
    staking_key_hash: bytes | None,
) -> None:
    if staking_key_hash and staking_path:
        raise INVALID_ADDRESS_PARAMETERS

    if staking_key_hash:
        if len(staking_key_hash) != ADDRESS_KEY_HASH_SIZE:
            raise INVALID_ADDRESS_PARAMETERS
    elif staking_path:
        if not SCHEMA_STAKING_ANY_ACCOUNT.match(staking_path):
            raise INVALID_ADDRESS_PARAMETERS
    else:
        raise INVALID_ADDRESS_PARAMETERS


def _validate_address_and_get_type(
    address: str, protocol_magic: int, network_id: int
) -> int:
    """
    Validates Cardano address and returns its type
    for the convenience of outward-facing functions.
    """
    if address is None or len(address) == 0:
        raise INVALID_ADDRESS

    address_bytes = get_address_bytes_unsafe(address)
    address_type = _get_address_type(address_bytes)

    if address_type == CardanoAddressType.BYRON:
        validate_byron_address(address_bytes, protocol_magic)
    elif address_type in ADDRESS_TYPES_SHELLEY:
        _validate_shelley_address(address, address_bytes, network_id)
    else:
        raise INVALID_ADDRESS

    return address_type


def validate_output_address(address: str, protocol_magic: int, network_id: int) -> None:
    address_type = _validate_address_and_get_type(address, protocol_magic, network_id)

    if address_type in (CardanoAddressType.REWARD, CardanoAddressType.REWARD_SCRIPT):
        raise INVALID_ADDRESS


def validate_reward_address(address: str, protocol_magic: int, network_id: int) -> None:
    address_type = _validate_address_and_get_type(address, protocol_magic, network_id)

    if address_type not in (
        CardanoAddressType.REWARD,
        CardanoAddressType.REWARD_SCRIPT,
    ):
        raise INVALID_ADDRESS


def get_address_bytes_unsafe(address: str) -> bytes:
    try:
        address_bytes = bech32.decode_unsafe(address)
    except ValueError:
        try:
            address_bytes = base58.decode(address)
        except ValueError:
            raise INVALID_ADDRESS

    return address_bytes


def _get_address_type(address: bytes) -> EnumTypeCardanoAddressType:
    return address[0] >> 4  # type: ignore


def _validate_shelley_address(
    address_str: str, address_bytes: bytes, network_id: int
) -> None:
    address_type = _get_address_type(address_bytes)

    _validate_address_size(address_bytes)
    _validate_address_bech32_hrp(address_str, address_type, network_id)
    _validate_address_network_id(address_bytes, network_id)


def _validate_address_size(address_bytes: bytes) -> None:
    if not (MIN_ADDRESS_BYTES_LENGTH <= len(address_bytes) <= MAX_ADDRESS_BYTES_LENGTH):
        raise INVALID_ADDRESS


def _validate_address_bech32_hrp(
    address_str: str, address_type: EnumTypeCardanoAddressType, network_id: int
) -> None:
    valid_hrp = _get_bech32_hrp_for_address(address_type, network_id)
    bech32_hrp = bech32.get_hrp(address_str)

    if valid_hrp != bech32_hrp:
        raise INVALID_ADDRESS


def _get_bech32_hrp_for_address(
    address_type: EnumTypeCardanoAddressType, network_id: int
) -> str:
    if address_type == CardanoAddressType.BYRON:
        # Byron address uses base58 encoding
        raise ValueError

    if (
        address_type == CardanoAddressType.REWARD
        or address_type == CardanoAddressType.REWARD_SCRIPT
    ):
        if network_ids.is_mainnet(network_id):
            return bech32.HRP_REWARD_ADDRESS
        else:
            return bech32.HRP_TESTNET_REWARD_ADDRESS
    else:
        if network_ids.is_mainnet(network_id):
            return bech32.HRP_ADDRESS
        else:
            return bech32.HRP_TESTNET_ADDRESS


def _validate_address_network_id(address: bytes, network_id: int) -> None:
    if _get_address_network_id(address) != network_id:
        raise NETWORK_MISMATCH


def _get_address_network_id(address: bytes) -> int:
    return address[0] & 0x0F


def get_public_key_hash(keychain: seed.Keychain, path: list[int]) -> bytes:
    public_key = derive_public_key(keychain, path)
    return hashlib.blake2b(data=public_key, outlen=ADDRESS_KEY_HASH_SIZE).digest()


def derive_human_readable_address(
    keychain: seed.Keychain,
    parameters: CardanoAddressParametersType,
    protocol_magic: int,
    network_id: int,
) -> str:
    from ubinascii import hexlify

    # hash = get_script_hash(parameters.script_payment)
    # print(hexlify(hash))
    # print(
    #     encode_human_readable_address(
    #         _derive_enterprise_address(keychain, parameters.address_n, network_id)
    #     )
    # )
    # print(
    #     hexlify(
    #         bech32.decode_unsafe(
    #             "addr1wyf7438h7etkh6uynvzlr052k54uj5zhkj9l32kpkzdkvwgypg4xe"
    #         )[1:]
    #     )
    # )

    address_bytes = derive_address_bytes(
        keychain, parameters, protocol_magic, network_id
    )

    return encode_human_readable_address(address_bytes)


def encode_human_readable_address(address_bytes: bytes) -> str:
    address_type = _get_address_type(address_bytes)
    if address_type == CardanoAddressType.BYRON:
        return base58.encode(address_bytes)
    elif address_type in ADDRESS_TYPES_SHELLEY:
        hrp = _get_bech32_hrp_for_address(
            address_type, _get_address_network_id(address_bytes)
        )
        return bech32.encode(hrp, address_bytes)
    else:
        raise ValueError


def derive_address_bytes(
    keychain: seed.Keychain,
    parameters: CardanoAddressParametersType,
    protocol_magic: int,
    network_id: int,
) -> bytes:
    is_byron_address = parameters.address_type == CardanoAddressType.BYRON

    if is_byron_address:
        address = derive_byron_address(keychain, parameters.address_n, protocol_magic)
    else:
        address = _derive_shelley_address(keychain, parameters, network_id)

    return address


def _derive_shelley_address(
    keychain: seed.Keychain, parameters: CardanoAddressParametersType, network_id: int
):
    header = _create_address_header(parameters.address_type, network_id)

    # TODO GK can payment part be script_staking? (e.g. for reward address)
    payment_part = _get_address_payment_part(keychain, parameters)
    staking_part = _get_address_staking_part(keychain, parameters)

    return header + payment_part + staking_part


def _create_address_header(
    address_type: EnumTypeCardanoAddressType, network_id: int
) -> bytes:
    header = address_type << 4 | network_id
    return header.to_bytes(1, "little")


def _get_address_payment_part(
    keychain: seed.Keychain, parameters: CardanoAddressParametersType
) -> bytes:
    if parameters.address_n:
        return get_public_key_hash(keychain, parameters.address_n)
    elif parameters.script_payment:
        return get_script_hash(keychain, parameters.script_payment)
    else:
        return bytes()


def _get_address_staking_part(
    keychain: seed.Keychain, parameters: CardanoAddressParametersType
) -> bytes:
    if parameters.staking_key_hash:
        return parameters.staking_key_hash
    elif parameters.address_n_staking:
        return get_public_key_hash(keychain, parameters.address_n_staking)
    elif parameters.script_staking:
        return get_script_hash(keychain, parameters.script_staking)
    elif parameters.certificate_pointer:
        return _encode_certificate_pointer(parameters.certificate_pointer)
    else:
        return bytes()


def _encode_certificate_pointer(pointer: CardanoBlockchainPointerType) -> bytes:
    block_index_encoded = variable_length_encode(pointer.block_index)
    tx_index_encoded = variable_length_encode(pointer.tx_index)
    certificate_index_encoded = variable_length_encode(pointer.certificate_index)

    return bytes(block_index_encoded + tx_index_encoded + certificate_index_encoded)


def pack_reward_address_bytes(
    staking_key_hash: bytes,
    network_id: int,
    is_script: bool,
) -> bytes:
    """
    Helper function to transform raw staking key hash into reward address
    """
    header = _create_address_header(
        CardanoAddressType.REWARD_SCRIPT if is_script else CardanoAddressType.REWARD,
        network_id,
    )

    return header + staking_key_hash
