from trezor.messages import CardanoVersion
import apps.cardano.byron.get_address as byron
import apps.cardano.shelley.get_address as shelley


async def get_address(ctx, msg):
    if msg.version is None or msg.version == CardanoVersion.BYRON:
        return await byron.get_address(ctx, msg)
    elif msg.version == CardanoVersion.SHELLEY:
        return await shelley.get_address(ctx, msg)

    raise ValueError("Unsupported Cardano version '%s'" % msg.version)
