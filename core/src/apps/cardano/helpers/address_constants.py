from trezor.messages import CardanoAddressType

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

_HEADER_LENGTH = 1
_HASH_LENGTH = 28
_SCRIPT_HASH_LENGTH = 28
_MIN_POINTER_SIZE = 0
_MAX_POINTER_SIZE = 12

ADDRESS_BYTES_MIN_LENGTHS = {
    CardanoAddressType.BASE: _HEADER_LENGTH + _HASH_LENGTH + _HASH_LENGTH,
    CardanoAddressType.BASE_SCRIPT_KEY: _HEADER_LENGTH
    + _SCRIPT_HASH_LENGTH
    + _HASH_LENGTH,
    CardanoAddressType.BASE_KEY_SCRIPT: _HEADER_LENGTH
    + _HASH_LENGTH
    + _SCRIPT_HASH_LENGTH,
    CardanoAddressType.BASE_SCRIPT_SCRIPT: _HEADER_LENGTH
    + _SCRIPT_HASH_LENGTH
    + _SCRIPT_HASH_LENGTH,
    CardanoAddressType.POINTER: _HEADER_LENGTH + _HASH_LENGTH + _MIN_POINTER_SIZE,
    CardanoAddressType.POINTER_SCRIPT: _HEADER_LENGTH
    + _SCRIPT_HASH_LENGTH
    + _MIN_POINTER_SIZE,
    CardanoAddressType.ENTERPRISE: _HEADER_LENGTH + _HASH_LENGTH,
    CardanoAddressType.ENTERPRISE_SCRIPT: _HEADER_LENGTH + _SCRIPT_HASH_LENGTH,
    CardanoAddressType.REWARD: _HEADER_LENGTH + _HASH_LENGTH,
    CardanoAddressType.REWARD_SCRIPT: _HEADER_LENGTH + _SCRIPT_HASH_LENGTH,
}

ADDRESS_BYTES_MAX_LENGTHS = {
    CardanoAddressType.BASE: ADDRESS_BYTES_MIN_LENGTHS[CardanoAddressType.BASE],
    CardanoAddressType.BASE_SCRIPT_KEY: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.BASE_SCRIPT_KEY
    ],
    CardanoAddressType.BASE_KEY_SCRIPT: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.BASE_KEY_SCRIPT
    ],
    CardanoAddressType.BASE_SCRIPT_SCRIPT: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.BASE_SCRIPT_SCRIPT
    ],
    CardanoAddressType.POINTER: _HEADER_LENGTH + _HASH_LENGTH + _MAX_POINTER_SIZE,
    CardanoAddressType.POINTER_SCRIPT: _HEADER_LENGTH
    + _SCRIPT_HASH_LENGTH
    + _MAX_POINTER_SIZE,
    CardanoAddressType.ENTERPRISE: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.ENTERPRISE
    ],
    CardanoAddressType.ENTERPRISE_SCRIPT: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.ENTERPRISE_SCRIPT
    ],
    CardanoAddressType.REWARD: ADDRESS_BYTES_MIN_LENGTHS[CardanoAddressType.REWARD],
    CardanoAddressType.REWARD_SCRIPT: ADDRESS_BYTES_MIN_LENGTHS[
        CardanoAddressType.REWARD_SCRIPT
    ],
}
