from typing import Type

from trezor import log, wire
from trezor.enums import CardanoTxSigningMode
from trezor.messages import CardanoSignTxFinished, CardanoSignTxInit

from .. import seed
from .multisig_signer import MultisigSigner
from .ordinary_signer import OrdinarySigner
from .plutus_signer import PlutusSigner
from .pool_owner_signer import PoolOwnerSigner
from .signer import Signer


@seed.with_keychain
async def sign_tx(
    ctx: wire.Context, msg: CardanoSignTxInit, keychain: seed.Keychain
) -> CardanoSignTxFinished:
    signer_types: dict[CardanoTxSigningMode, Type[Signer]] = {
        CardanoTxSigningMode.ORDINARY_TRANSACTION: OrdinarySigner,
        CardanoTxSigningMode.POOL_REGISTRATION_AS_OWNER: PoolOwnerSigner,
        CardanoTxSigningMode.MULTISIG_TRANSACTION: MultisigSigner,
        CardanoTxSigningMode.PLUTUS_TRANSACTION: PlutusSigner,
    }
    signer_type = signer_types[msg.signing_mode]

    signer = signer_type(ctx, msg, keychain)

    try:
        await signer.sign()
    except ValueError as e:
        if __debug__:
            log.exception(__name__, e)
        raise wire.ProcessError("Signing failed")

    return CardanoSignTxFinished()
