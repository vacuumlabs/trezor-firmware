from trezor import log, wire
from trezor.messages import CardanoAddress

from . import seed
from .address import derive_human_readable_address, validate_address_parameters
from .helpers.address_credential_policy import (
    ADDRESS_POLICY_SHOW_SPLIT,
    get_address_policy,
    get_payment_credential_policy,
    get_stake_credential_policy,
)
from .layout import show_cardano_address, show_set_credential
from .sign_tx import validate_network_info

if False:
    from trezor.messages import (
        CardanoAddressParametersType,
        CardanoGetAddress,
    )


@seed.with_keychain
async def get_address(
    ctx: wire.Context, msg: CardanoGetAddress, keychain: seed.Keychain
) -> CardanoAddress:
    address_parameters = msg.address_parameters

    validate_network_info(msg.network_id, msg.protocol_magic)
    validate_address_parameters(address_parameters)

    try:
        address = derive_human_readable_address(
            keychain, address_parameters, msg.protocol_magic, msg.network_id
        )
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Deriving address failed")

    if msg.show_display:
        await _display_address(
            ctx, keychain, address_parameters, address, msg.protocol_magic
        )

    return CardanoAddress(address=address)


async def _display_address(
    ctx: wire.Context,
    keychain: seed.Keychain,
    address_parameters: CardanoAddressParametersType,
    address: str,
    protocol_magic: int,
) -> None:
    address_policy = get_address_policy(keychain, address_parameters)
    if address_policy == ADDRESS_POLICY_SHOW_SPLIT:
        await show_set_credential(
            ctx,
            address_parameters.address_n,
            None,
            address_parameters.script_payment_hash,
            address_parameters.certificate_pointer,
            address_parameters.address_type,
            get_payment_credential_policy(address_parameters),
            "payment",
        )
        await show_set_credential(
            ctx,
            address_parameters.address_n_staking,
            address_parameters.staking_key_hash,
            address_parameters.script_staking_hash,
            address_parameters.certificate_pointer,
            address_parameters.address_type,
            get_stake_credential_policy(keychain, address_parameters),
            "stake",
        )

    await show_cardano_address(ctx, address_parameters, address, protocol_magic)
