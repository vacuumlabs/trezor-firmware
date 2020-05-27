from micropython import const

from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.strings import format_amount
from trezor.ui.button import ButtonDefault
from trezor.ui.scroll import Paginated
from trezor.ui.text import Text
from trezor.utils import chunks

from apps.common.layout import show_warning
from apps.common.confirm import confirm, hold_to_confirm

if False:
    from trezor import wire
    from trezor.messages import CardanoCertificatePointerType

def format_coin_amount(amount: int) -> str:
    return "%s %s" % (format_amount(amount, 6), "ADA")


async def confirm_sending(ctx: wire.Context, amount: int, to: str) -> bool:
    to_lines = list(chunks(to, 17))

    t1 = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN)
    t1.normal("Confirm sending:")
    t1.bold(format_coin_amount(amount))
    t1.normal("to:")
    t1.bold(to_lines[0])

    PER_PAGE = const(4)
    pages = [t1]
    if len(to_lines) > 1:
        to_pages = list(chunks(to_lines[1:], PER_PAGE))
        for page in to_pages:
            t = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN)
            for line in page:
                t.bold(line)
            pages.append(t)

    return await confirm(ctx, Paginated(pages))


async def confirm_transaction(ctx: wire.Context, amount: int, fee: int, network_name: str) -> bool:
    t1 = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN)
    t1.normal("Total amount:")
    t1.bold(format_coin_amount(amount))
    t1.normal("including fee:")
    t1.bold(format_coin_amount(fee))

    t2 = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN)
    t2.normal("Network:")
    t2.bold(network_name)

    return await hold_to_confirm(ctx, Paginated([t1, t2]))


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
