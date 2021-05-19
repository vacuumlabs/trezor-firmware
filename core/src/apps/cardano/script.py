from trezor.crypto import hashlib
from trezor.messages import CardanoAddressType, CardanoScriptT, CardanoScriptType

from apps.cardano.helpers import ADDRESS_KEY_HASH_SIZE, INVALID_SCRIPT
from apps.common import cbor

from .helpers.paths import SCHEMA_ADDRESS, SCHEMA_STAKING_ANY_ACCOUNT
from .helpers.utils import derive_public_key
from .seed import Keychain, is_multisig_path

SCRIPT_ADDRESS_TYPES = (
    CardanoAddressType.BASE_SCRIPT_KEY,
    CardanoAddressType.BASE_KEY_SCRIPT,
    CardanoAddressType.BASE_SCRIPT_SCRIPT,
    CardanoAddressType.POINTER_SCRIPT,
    CardanoAddressType.ENTERPRISE_SCRIPT,
    CardanoAddressType.REWARD_SCRIPT,
)

# TODO GK unit tests
def validate_script(script: CardanoScriptT | None) -> None:
    if not script:
        raise INVALID_SCRIPT

    if script.type == CardanoScriptType.PUB_KEY:
        if script.key_hash and script.key_path:
            raise INVALID_SCRIPT
        if script.key_hash:
            if len(script.key_hash) != ADDRESS_KEY_HASH_SIZE:
                raise INVALID_SCRIPT
        elif script.key_path:
            if not SCHEMA_ADDRESS.match(
                script.key_path
            ) and not SCHEMA_STAKING_ANY_ACCOUNT.match(script.key_path):
                raise INVALID_SCRIPT
            if not is_multisig_path(script.key_path):
                raise INVALID_SCRIPT
        else:
            raise INVALID_SCRIPT
    elif script.type == CardanoScriptType.ALL:
        if not script.scripts:
            raise INVALID_SCRIPT
        for sub_script in script.scripts:
            validate_script(sub_script)
    elif script.type == CardanoScriptType.ANY:
        if not script.scripts:
            raise INVALID_SCRIPT
        for sub_script in script.scripts:
            validate_script(sub_script)
    elif script.type == CardanoScriptType.N_OF_K:
        if not script.required:
            raise INVALID_SCRIPT
        if not script.scripts:
            raise INVALID_SCRIPT
        for sub_script in script.scripts:
            validate_script(sub_script)
    elif script.type == CardanoScriptType.INVALID_BEFORE:
        if not script.invalid_before:
            raise INVALID_SCRIPT
    elif script.type == CardanoScriptType.INVALID_HEREAFTER:
        if not script.invalid_hereafter:
            raise INVALID_SCRIPT


def get_script_hash(keychain: Keychain, script: CardanoScriptT) -> bytes:
    script_cbor = cbor.encode(cborize_script(keychain, script))
    prefixed_script_cbor = b"\00" + script_cbor
    return hashlib.blake2b(data=prefixed_script_cbor, outlen=28).digest()


# TODO GK return type
def cborize_script(keychain: Keychain, script: CardanoScriptT):
    script_content = []
    if script.type == CardanoScriptType.PUB_KEY:
        # TODO GK or path
        if script.key_hash:
            script_content = [script.key_hash]
        elif script.key_path:
            script_content = [derive_public_key(keychain, script.key_path)]
    elif script.type == CardanoScriptType.ALL:
        script_content = [
            [cborize_script(keychain, sub_script) for sub_script in script.scripts]
        ]
    elif script.type == CardanoScriptType.ANY:
        script_content = [
            [cborize_script(keychain, sub_script) for sub_script in script.scripts]
        ]
    elif script.type == CardanoScriptType.N_OF_K:
        # TODO GK rename script.required
        script_content = [
            script.required,
            [cborize_script(keychain, sub_script) for sub_script in script.scripts],
        ]
    elif script.type == CardanoScriptType.INVALID_BEFORE:
        script_content = [script.invalid_before]
    elif script.type == CardanoScriptType.INVALID_HEREAFTER:
        script_content = [script.invalid_hereafter]

    return [script.type] + script_content
