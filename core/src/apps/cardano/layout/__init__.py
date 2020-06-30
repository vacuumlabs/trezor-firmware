from micropython import const
from ubinascii import hexlify

from trezor import ui
from trezor.messages import ButtonRequestType, CardanoCertificateType
from trezor.strings import format_amount
from trezor.ui.button import ButtonDefault
from trezor.ui.scroll import Paginated
from trezor.ui.text import Text
from trezor.utils import chunks

from apps.common.layout import address_n_to_str, show_warning
from apps.common.confirm import confirm, require_confirm, require_hold_to_confirm

if False:
    from trezor import wire
    from trezor.messages import CardanoCertificatePointerType, CardanoTxCertificateType


def format_coin_amount(amount: int) -> str:
    return "%s %s" % (format_amount(amount, 6), "ADA")


def _create_text_with_transaction_heading():
    return Text("Confirm transaction", ui.ICON_SEND, ui.GREEN)


async def confirm_sending(ctx: wire.Context, amount: int, to: str) -> None:
    to_lines = list(chunks(to, 17))

    t1 = _create_text_with_transaction_heading()
    t1.normal("Confirm sending:")
    t1.bold(format_coin_amount(amount))
    t1.normal("to")
    t1.bold(to_lines[0])

    PER_PAGE = const(4)
    pages = [t1]
    if len(to_lines) > 1:
        to_pages = list(chunks(to_lines[1:], PER_PAGE))
        for page in to_pages:
            t = _create_text_with_transaction_heading()
            for line in page:
                t.bold(line)
            pages.append(t)

    await require_confirm(ctx, Paginated(pages))


async def confirm_transaction(
    ctx: wire.Context,
    amount: int,
    fee: int,
    network_name: str,
    certificates: List[CardanoTxCertificateType],
) -> None:
    pages = []

    t1 = _create_text_with_transaction_heading()
    t1.normal("Transaction amount:")
    t1.bold(format_coin_amount(amount))
    t1.normal("Transaction fee:")
    t1.bold(format_coin_amount(fee))
    pages.append(t1)

    # todo: GK - deposit??

    if len(certificates) > 0:
        t2 = _create_text_with_transaction_heading()
        t2.normal("Certificates:")
        for certificate in certificates:
            t2.bold(_format_certificate_type(certificate.type))
        pages.append(t2)

    t3 = _create_text_with_transaction_heading()
    t3.normal("Network:")
    t3.bold(network_name)
    pages.append(t3)

    await require_hold_to_confirm(ctx, Paginated(pages))


async def confirm_certificate(
    ctx: wire.Context, certificate: CardanoTxCertificateType
) -> bool:
    pages = []

    t1 = _create_text_with_transaction_heading()
    t1.normal("Confirm:")
    t1.bold(_format_certificate_type(certificate.type))
    t1.normal("for account:")
    t1.bold(address_n_to_str(certificate.path[:3]))
    pages.append(t1)

    if certificate.type == CardanoCertificateType.STAKE_DELEGATION:
        t2 = _create_text_with_transaction_heading()
        t2.normal("to pool:")
        t2.bold(hexlify(certificate.pool).decode())
        pages.append(t2)

    await require_confirm(ctx, Paginated(pages))


def _format_certificate_type(certificate_type: int) -> str:
    if certificate_type == CardanoCertificateType.STAKE_REGISTRATION:
        return "Stake key registration"
    elif certificate_type == CardanoCertificateType.STAKE_DEREGISTRATION:
        return "Stake key deregistration"
    elif certificate_type == CardanoCertificateType.STAKE_DELEGATION:
        return "Stake delegation"
    else:
        raise ValueError("Unknown certificate type")


async def show_address(
    ctx, address: str, desc: str = "Confirm address", network: str = None
) -> bool:
    """
    Custom show_address function is needed because cardano addresses don't
    fit on a single screen.
    """
    pages = []
    for lines in chunks(list(chunks(address, 16)), 5):
        text = Text(desc, ui.ICON_RECEIVE, ui.GREEN)
        if network is not None:
            text.normal("%s network" % network)
        text.mono(*lines)
        pages.append(text)

    return await confirm(
        ctx,
        Paginated(pages),
        code=ButtonRequestType.Address,
        cancel="QR",
        cancel_style=ButtonDefault,
    )


async def show_staking_key_warnings(
    ctx, stakin_key_hash: str, account_path: str
) -> None:
    await show_warning(
        ctx,
        (
            "Staking key associated",
            "with this address does",
            "not belong to your",
            "account",
            account_path,
        ),
        button="Ok",
    )
    await show_warning(
        ctx, ("Staking key:", stakin_key_hash,), button="Ok",
    )


async def show_pointer_address_warning(
    ctx, pointer: CardanoCertificatePointerType
) -> None:
    await show_warning(
        ctx,
        (
            "Pointer address:",
            "Block: %s" % pointer.block_index,
            "Transaction: %s" % pointer.tx_index,
            "Certificate: %s" % pointer.certificate_index,
        ),
        button="Ok",
    )
