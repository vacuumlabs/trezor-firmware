from trezor import log, wire
from trezor.messages.CardanoScriptHash import CardanoScriptHash

from . import script, seed
from .helpers import bech32
from .layout import show_human_readable_script_hash, show_script

if False:
    from trezor.messages.CardanoGetScriptHash import CardanoGetScriptHash


@seed.with_keychain
async def get_script_hash(
    ctx: wire.Context, msg: CardanoGetScriptHash, keychain: seed.Keychain
) -> CardanoScriptHash:
    script.validate_script(msg.script)

    try:
        script_hash = script.get_script_hash(keychain, msg.script)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Getting script hash failed")

    if msg.show_display:
        await show_script(ctx, msg.script)
        # TODO GK show human readable? or bytes? or something else?
        await show_human_readable_script_hash(
            ctx, bech32.encode(bech32.HRP_SCRIPT_HASH, script_hash)
        )

    return CardanoScriptHash(script_hash=script_hash)
