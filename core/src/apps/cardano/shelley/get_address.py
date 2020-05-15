from trezor import log, wire
from trezor.messages.CardanoAddress import CardanoAddress
from trezor.messages import CardanoAddressType

from apps.cardano.shelley import CURVE, seed
from apps.cardano.shelley.address import validate_full_path, get_base_address, get_enterprise_address, get_pointer_address, get_bootstrap_address
from apps.common import paths
from apps.common.layout import address_n_to_str, show_address, show_qr


async def get_address(ctx, msg):
    keychain = await seed.get_keychain(ctx, msg.address_n[:2])

    await paths.validate_path(ctx, validate_full_path, keychain, msg.address_n, CURVE)

    try:
        address = _get_address(keychain, msg)
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Deriving address failed")
    if msg.show_display:
        desc = address_n_to_str(msg.address_n)
        while True:
            if await show_address(ctx, address, desc=desc):
                break
            if await show_qr(ctx, address, desc=desc):
                break

    return CardanoAddress(address=address)


def _get_address(keychain, msg):
    if msg.address_type == CardanoAddressType.BASE_ADDRESS:
        return get_base_address(keychain, msg.address_n, msg.network_id)
    if msg.address_type == CardanoAddressType.ENTERPRISE_ADDRESS:
        return get_enterprise_address(keychain, msg.address_n, msg.network_id)
    if msg.address_type == CardanoAddressType.POINTER_ADDRESS:
        return get_pointer_address(keychain, msg.address_n, msg.network_id, msg.block_index, msg.tx_index, msg.certificate_index)
    if msg.address_type == CardanoAddressType.BOOTSTRAP_ADDRESS:
        return get_bootstrap_address(keychain, msg.address_n)
