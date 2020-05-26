from ubinascii import hexlify

from trezor import log, wire
from trezor.messages import CardanoAddressType
from trezor.messages.CardanoAddress import CardanoAddress

from apps.cardano import CURVE, seed
from apps.cardano.address import (
    get_base_address,
    get_bootstrap_address,
    get_enterprise_address,
    get_pointer_address,
    get_staking_key_hash,
    validate_full_path,
)
from apps.cardano.layout import (
    show_address,
    show_pointer_address_warning,
    show_staking_key_warnings,
)
from apps.common import paths
from apps.common.layout import address_n_to_str, show_qr

if False:
    from trezor.messages.CardanoGetAddress import CardanoGetAddress


async def get_address(ctx: wire.Context, msg: CardanoGetAddress) -> CardanoAddress:
    keychain = await seed.get_keychain(ctx, msg.address_n[:2])

    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)

    try:
        address = _get_address(keychain, msg)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Deriving address failed")

    if msg.show_display:
        await _display_address(ctx, msg, keychain, address)

    return CardanoAddress(address=address)


async def _display_address(
    ctx: wire.Context, msg: CardanoGetAddress, keychain: seed.Keychain, address: str
) -> None:
    await _show_warnings_if_applicable(ctx, msg, keychain)

    desc = address_n_to_str(msg.address_n)
    while True:
        if await show_address(ctx, address, desc=desc):
            break
        if await show_qr(ctx, address, desc=desc):
            break


async def _show_warnings_if_applicable(
    ctx: wire.Context, msg: CardanoGetAddress, keychain: seed.Keychain
):
    if msg.staking_key_hash is not None:
        account_staking_key_hash = get_staking_key_hash(keychain, msg.address_n)
        if msg.staking_key_hash != account_staking_key_hash:
            hash_str = hexlify(msg.staking_key_hash).decode()
            account_path = address_n_to_str(msg.address_n[:3])
            await show_staking_key_warnings(ctx, hash_str, account_path)
    elif msg.address_type == CardanoAddressType.POINTER_ADDRESS:
        await show_pointer_address_warning(
            ctx, msg.block_index, msg.tx_index, msg.certificate_index
        )


def _get_address(keychain: seed.Keychain, msg: CardanoGetAddress) -> str:
    if msg.address_type == CardanoAddressType.BASE_ADDRESS:
        return get_base_address(
            keychain, msg.address_n, msg.network_id, msg.staking_key_hash
        )
    elif msg.address_type == CardanoAddressType.ENTERPRISE_ADDRESS:
        return get_enterprise_address(keychain, msg.address_n, msg.network_id)
    elif msg.address_type == CardanoAddressType.POINTER_ADDRESS:
        return get_pointer_address(
            keychain,
            msg.address_n,
            msg.network_id,
            msg.block_index,
            msg.tx_index,
            msg.certificate_index,
        )
    elif msg.address_type == CardanoAddressType.BOOTSTRAP_ADDRESS:
        return get_bootstrap_address(keychain, msg.address_n)
    else:
        raise ValueError("Invalid address type '%s'" % msg.address_type)
