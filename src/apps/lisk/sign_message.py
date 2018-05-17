from .helpers import LISK_CURVE, get_address_from_public_key
from apps.wallet.sign_message import require_confirm_sign_message

async def lisk_sign_message(ctx, msg):
    from trezor.messages.LiskMessageSignature import LiskMessageSignature
    from trezor.crypto.curve import ed25519
    from ..common import seed

    message = msg.message

    await require_confirm_sign_message(ctx, message)

    address_n = msg.address_n or ()
    node = await seed.derive_node(ctx, address_n, LISK_CURVE)

    seckey = node.private_key()
    public_key = ed25519.publickey(seckey)
    address = get_address_from_public_key(public_key)

    signature = ed25519.sign(seckey, message)

    return LiskMessageSignature(address=address, signature=signature)
