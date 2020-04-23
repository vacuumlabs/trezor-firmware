from trezor.messages import CardanoVersion
import apps.cardano.byron.get_public_key as byron
import apps.cardano.shelley.get_public_key as shelley


async def get_public_key(ctx, msg):
    if msg.version is None or msg.version == CardanoVersion.BYRON:
        return await byron.get_public_key(ctx, msg)
    elif msg.version == CardanoVersion.SHELLEY:
        return await shelley.get_public_key(ctx, msg)

    raise ValueError("Unsupported Cardano version '%s'" % msg.version)
