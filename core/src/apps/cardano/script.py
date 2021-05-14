from trezor.crypto import hashlib
from trezor.messages import CardanoAddressType, CardanoScriptT, CardanoScriptType

from apps.cardano.helpers import ADDRESS_KEY_HASH_SIZE, INVALID_SCRIPT
from apps.common import cbor

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
        # TODO GK or path
        if len(script.key_hash) != ADDRESS_KEY_HASH_SIZE:
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


def get_script_hash(script: CardanoScriptT) -> bytes:
    script_cbor = cbor.encode(cborize_script(script))
    prefixed_script_cbor = b"\00" + script_cbor
    return hashlib.blake2b(data=prefixed_script_cbor, outlen=28).digest()


# TODO GK return type
def cborize_script(script: CardanoScriptT):
    script_content = []
    if script.type == CardanoScriptType.PUB_KEY:
        # TODO GK or path
        script_content = [script.key_hash]
    elif script.type == CardanoScriptType.ALL:
        script_content = [[cborize_script(sub_script) for sub_script in script.scripts]]
    elif script.type == CardanoScriptType.ANY:
        script_content = [[cborize_script(sub_script) for sub_script in script.scripts]]
    elif script.type == CardanoScriptType.N_OF_K:
        # TODO GK rename script.required
        script_content = [
            script.required,
            [cborize_script(sub_script) for sub_script in script.scripts],
        ]
    elif script.type == CardanoScriptType.INVALID_BEFORE:
        script_content = [script.invalid_before]
    elif script.type == CardanoScriptType.INVALID_HEREAFTER:
        script_content = [script.invalid_hereafter]

    return [script.type] + script_content


# TODO GK
def show_script(script: CardanoScriptT) -> None:
    pass
