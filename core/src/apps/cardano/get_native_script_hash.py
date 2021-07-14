from trezor import log, wire
from trezor.messages import CardanoNativeScriptHash

from . import native_script, seed
from .helpers import bech32
from .layout import show_human_readable_script_hash, show_native_script

if False:
    from trezor.messages import CardanoGetNativeScriptHash


@seed.with_keychain
async def get_native_script_hash(
    ctx: wire.Context, msg: CardanoGetNativeScriptHash, keychain: seed.Keychain
) -> CardanoNativeScriptHash:
    native_script.validate_native_script(msg.script)

    try:
        script_hash = native_script.get_native_script_hash(keychain, msg.script)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Getting native script hash failed")

    if msg.show_display:
        await show_native_script(ctx, msg.script)
        await show_human_readable_script_hash(
            ctx, bech32.encode(bech32.HRP_SCRIPT_HASH, script_hash)
        )

    return CardanoNativeScriptHash(script_hash=script_hash)
