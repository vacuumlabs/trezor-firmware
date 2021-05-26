from trezor.crypto import hashlib
from trezor.messages import CardanoAddressType, CardanoScriptType

from apps.cardano.helpers import ADDRESS_KEY_HASH_SIZE, INVALID_SCRIPT
from apps.common import cbor

from .helpers.paths import SCHEMA_ADDRESS, SCHEMA_STAKING_ANY_ACCOUNT
from .helpers.utils import get_public_key_hash
from .seed import Keychain, is_multisig_path

if False:
    from typing import Any

    from trezor.messages.CardanoScript import CardanoScript

    from apps.common.cbor import CborSequence

SCRIPT_ADDRESS_TYPES = (
    CardanoAddressType.BASE_SCRIPT_KEY,
    CardanoAddressType.BASE_KEY_SCRIPT,
    CardanoAddressType.BASE_SCRIPT_SCRIPT,
    CardanoAddressType.POINTER_SCRIPT,
    CardanoAddressType.ENTERPRISE_SCRIPT,
    CardanoAddressType.REWARD_SCRIPT,
)


def validate_script(script: CardanoScript | None) -> None:
    if not script:
        raise INVALID_SCRIPT

    _validate_script_structure(script)

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
        if not script.required_signatures_count:
            raise INVALID_SCRIPT
        if not script.scripts:
            raise INVALID_SCRIPT
        for sub_script in script.scripts:
            validate_script(sub_script)
    elif script.type == CardanoScriptType.INVALID_BEFORE:
        if script.invalid_before is None:
            raise INVALID_SCRIPT
    elif script.type == CardanoScriptType.INVALID_HEREAFTER:
        if script.invalid_hereafter is None:
            raise INVALID_SCRIPT


def _validate_script_structure(script: CardanoScript) -> None:
    key_hash = script.key_hash
    key_path = script.key_path
    scripts = script.scripts
    required_signatures_count = script.required_signatures_count
    invalid_before = script.invalid_before
    invalid_hereafter = script.invalid_hereafter

    fields_to_be_empty: dict[int, list[Any]] = {
        CardanoScriptType.PUB_KEY: (
            scripts,
            required_signatures_count,
            invalid_before,
            invalid_hereafter,
        ),
        CardanoScriptType.ALL: (
            key_hash,
            key_path,
            required_signatures_count,
            invalid_before,
            invalid_hereafter,
        ),
        CardanoScriptType.ANY: (
            key_hash,
            key_path,
            required_signatures_count,
            invalid_before,
            invalid_hereafter,
        ),
        CardanoScriptType.N_OF_K: (
            key_hash,
            key_path,
            invalid_before,
            invalid_hereafter,
        ),
        CardanoScriptType.INVALID_BEFORE: (
            key_hash,
            key_path,
            required_signatures_count,
            invalid_hereafter,
        ),
        CardanoScriptType.INVALID_HEREAFTER: (
            key_hash,
            key_path,
            required_signatures_count,
            invalid_before,
        ),
    }

    if script.type not in fields_to_be_empty or any(fields_to_be_empty[script.type]):
        raise INVALID_SCRIPT


def get_script_hash(keychain: Keychain, script: CardanoScript) -> bytes:
    script_cbor = cbor.encode(cborize_script(keychain, script))
    prefixed_script_cbor = b"\00" + script_cbor
    return hashlib.blake2b(data=prefixed_script_cbor, outlen=28).digest()


def cborize_script(keychain: Keychain, script: CardanoScript) -> CborSequence:
    script_content: CborSequence
    if script.type == CardanoScriptType.PUB_KEY:
        if script.key_hash:
            script_content = (script.key_hash,)
        elif script.key_path:
            script_content = (get_public_key_hash(keychain, script.key_path),)
        else:
            raise INVALID_SCRIPT
    elif script.type == CardanoScriptType.ALL:
        script_content = (
            tuple(
                cborize_script(keychain, sub_script) for sub_script in script.scripts
            ),
        )
    elif script.type == CardanoScriptType.ANY:
        script_content = (
            tuple(
                cborize_script(keychain, sub_script) for sub_script in script.scripts
            ),
        )
    elif script.type == CardanoScriptType.N_OF_K:
        script_content = (
            script.required_signatures_count,
            tuple(
                cborize_script(keychain, sub_script) for sub_script in script.scripts
            ),
        )
    elif script.type == CardanoScriptType.INVALID_BEFORE:
        script_content = (script.invalid_before,)
    elif script.type == CardanoScriptType.INVALID_HEREAFTER:
        script_content = (script.invalid_hereafter,)
    else:
        raise INVALID_SCRIPT

    return (script.type,) + script_content
