from trezor.messages import CardanoVersion
import apps.cardano.byron.sign_tx as byron
import apps.cardano.shelley.sign_tx as shelley


async def sign_tx(ctx, msg):
    if msg.version is None or msg.version == CardanoVersion.BYRON:
        return await byron.sign_tx(ctx, msg)
    elif msg.version == CardanoVersion.SHELLEY:
        return await shelley.sign_tx(ctx, msg)

    raise ValueError("Unsupported Cardano version '%s'" % msg.version)
