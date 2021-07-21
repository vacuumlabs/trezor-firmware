from trezor import ui
from trezor.enums import (
    ButtonRequestType,
    CardanoAddressType,
    CardanoCertificateType,
    CardanoNativeScriptType,
    CardanoTxSigningMode,
)
from trezor.messages import CardanoAddressParametersType
from trezor.strings import format_amount
from trezor.ui.layouts import (
    confirm_metadata,
    confirm_output,
    confirm_path_warning,
    confirm_properties,
    show_address,
)

from apps.common.layout import address_n_to_str

from . import seed
from .address import derive_human_readable_address
from .helpers import protocol_magics
from .helpers.address_credential_policy import (
    CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL,
    CREDENTIAL_POLICY_SHOW_CHANGE,
    CREDENTIAL_POLICY_SHOW_OUTPUT,
    CREDENTIAL_POLICY_WARN_MISMATCH,
    CREDENTIAL_POLICY_WARN_NO_STAKING,
    CREDENTIAL_POLICY_WARN_REWARD_ADDRESS,
    CREDENTIAL_POLICY_WARN_SCRIPT,
)
from .helpers.utils import (
    format_account_number,
    format_asset_fingerprint,
    format_credential,
    format_optional_int,
    format_script_hash,
    format_stake_pool_id,
    get_set_credential,
    get_set_credential_title,
    to_account_path,
)

if False:
    from trezor import wire
    from trezor.messages import (
        CardanoBlockchainPointerType,
        CardanoTxCertificate,
        CardanoTxWithdrawal,
        CardanoPoolParametersType,
        CardanoPoolOwner,
        CardanoPoolMetadataType,
        CardanoNativeScript,
        CardanoToken,
        CardanoTxScriptWitnessRequest,
    )

    from trezor.ui.layouts import PropertyType


ADDRESS_TYPE_NAMES = {
    CardanoAddressType.BYRON: "Legacy",
    CardanoAddressType.BASE: "Base",
    CardanoAddressType.BASE_SCRIPT_KEY: "Base",
    CardanoAddressType.BASE_KEY_SCRIPT: "Base",
    CardanoAddressType.BASE_SCRIPT_SCRIPT: "Base",
    CardanoAddressType.POINTER: "Pointer",
    CardanoAddressType.POINTER_SCRIPT: "Pointer",
    CardanoAddressType.ENTERPRISE: "Enterprise",
    CardanoAddressType.ENTERPRISE_SCRIPT: "Enterprise",
    CardanoAddressType.REWARD: "Reward",
    CardanoAddressType.REWARD_SCRIPT: "Reward",
}

SCRIPT_TYPE_NAMES = {
    CardanoNativeScriptType.PUB_KEY: "Key",
    CardanoNativeScriptType.ALL: "All",
    CardanoNativeScriptType.ANY: "Any",
    CardanoNativeScriptType.N_OF_K: "N of K",
    CardanoNativeScriptType.INVALID_BEFORE: "Invalid before",
    CardanoNativeScriptType.INVALID_HEREAFTER: "Invalid hereafter",
}

CERTIFICATE_TYPE_NAMES = {
    CardanoCertificateType.STAKE_REGISTRATION: "Stake key registration",
    CardanoCertificateType.STAKE_DEREGISTRATION: "Stake key deregistration",
    CardanoCertificateType.STAKE_DELEGATION: "Stake delegation",
    CardanoCertificateType.STAKE_POOL_REGISTRATION: "Stakepool registration",
}


def format_coin_amount(amount: int) -> str:
    return "%s %s" % (format_amount(amount, 6), "ADA")


def is_printable_ascii_bytestring(bytestr: bytes) -> bool:
    return all((32 < b < 127) for b in bytestr)


async def show_native_script(
    ctx: wire.Context,
    script: CardanoNativeScript,
    indices: list[int] = [],
) -> None:
    indices_str = ".".join([str(i) for i in indices])

    props: list[PropertyType] = [
        (
            "Script%s:" % (" " + indices_str if indices_str else ""),
            SCRIPT_TYPE_NAMES[script.type].lower(),
        )
    ]

    if script.type in (
        CardanoNativeScriptType.ALL,
        CardanoNativeScriptType.ANY,
        CardanoNativeScriptType.N_OF_K,
    ):
        assert script.scripts  # validate_script
        props.append(("Confirm %i nested scripts" % len(script.scripts), None))

    if script.type == CardanoNativeScriptType.PUB_KEY:
        assert script.key_hash is not None or script.key_path  # validate_script
        if script.key_hash:
            props.append(("Key:", script.key_hash))
        elif script.key_path:
            props.append(("Key path: %s" % address_n_to_str(script.key_path), None))
    elif script.type == CardanoNativeScriptType.N_OF_K:
        assert script.required_signatures_count is not None  # validate_script
        props.append(
            ("Required signatures: %s" % script.required_signatures_count, None)
        )
    elif script.type == CardanoNativeScriptType.INVALID_BEFORE:
        assert script.invalid_before is not None  # validate_script
        props.append(("Invalid before: %s" % script.invalid_before, None))
    elif script.type == CardanoNativeScriptType.INVALID_HEREAFTER:
        assert script.invalid_hereafter is not None  # validate_script
        props.append(("Invalid hereafter: %s" % script.invalid_hereafter, None))

    await confirm_properties(
        ctx,
        "verify_script",
        title="Verify script",
        props=props,
        br_code=ButtonRequestType.Other,
    )

    for i, sub_script in enumerate(script.scripts):
        await show_native_script(ctx, sub_script, indices + [(i + 1)])


# TODO pass in script_hash and use format_script_hash
async def show_human_readable_script_hash(
    ctx: wire.Context, human_readable_script_hash: str
) -> None:
    await confirm_properties(
        ctx,
        "verify_script",
        title="Verify script",
        props=[("Script hash:", human_readable_script_hash)],
        br_code=ButtonRequestType.Other,
    )


async def show_transaction_signing_mode(
    ctx: wire.Context, signing_mode: CardanoTxSigningMode
) -> None:
    if signing_mode == CardanoTxSigningMode.MULTISIG_TRANSACTION:
        await confirm_metadata(
            ctx,
            "confirm_signing_mode",
            title="Confirm transaction",
            content="Confirming a multisig transaction.",
            larger_vspace=True,
            br_code=ButtonRequestType.Other,
        )


async def confirm_sending(
    ctx: wire.Context,
    ada_amount: int,
    to: str,
    is_change_output: bool,
) -> None:
    subtitle = "Change amount:" if is_change_output else "Confirm sending:"
    await confirm_output(
        ctx,
        to,
        format_coin_amount(ada_amount),
        title="Confirm transaction",
        subtitle=subtitle,
        font_amount=ui.BOLD,
        width_paginated=17,
        to_str="\nto\n",
        to_paginated=True,
        br_code=ButtonRequestType.Other,
    )


async def confirm_sending_token(
    ctx: wire.Context, policy_id: bytes, token: CardanoToken
) -> None:
    assert token.amount is not None  # _validate_token

    await confirm_properties(
        ctx,
        "confirm_token",
        title="Confirm transaction",
        props=[
            (
                "Asset fingerprint:",
                format_asset_fingerprint(
                    policy_id=policy_id,
                    asset_name_bytes=token.asset_name_bytes,
                ),
            ),
            ("Amount sent:", format_amount(token.amount, 0)),
        ],
        br_code=ButtonRequestType.Other,
    )


async def show_output_payment_credential(
    ctx: wire.Context,
    path: list[int],
    script_hash: bytes | None,
    address_type: CardanoAddressType,
    credential_policy: int,
) -> None:
    await show_credential(
        ctx, path, None, script_hash, None, address_type, credential_policy, "payment"
    )


async def show_output_stake_credential(
    ctx: wire.Context,
    path: list[int],
    key_hash: bytes | None,
    script_hash: bytes | None,
    pointer: CardanoBlockchainPointerType | None,
    address_type: CardanoAddressType,
    credential_policy: int,
) -> None:
    await show_credential(
        ctx,
        path,
        key_hash,
        script_hash,
        pointer,
        address_type,
        credential_policy,
        "stake",
    )


async def show_credential(
    ctx: wire.Context,
    path: list[int],
    key_hash: bytes | None,
    script_hash: bytes | None,
    pointer: CardanoBlockchainPointerType | None,
    address_type: CardanoAddressType,
    credential_policy: int,
    credential_usage: str,
) -> None:
    props: list[PropertyType] = []

    credential = get_set_credential(path, key_hash, script_hash, pointer)
    if credential:
        if (credential_policy & CREDENTIAL_POLICY_SHOW_CHANGE) != 0:
            address_usage = "Change address"
        elif (credential_policy & CREDENTIAL_POLICY_SHOW_OUTPUT) != 0:
            address_usage = "Output address"
        else:
            address_usage = "Address"

        credential_title = get_set_credential_title(
            path, key_hash, script_hash, pointer
        )
        props.append(
            (
                "%s %s credential is a %s:"
                % (address_usage, credential_usage, credential_title),
                None,
            )
        )
        props.extend(format_credential(path, key_hash, script_hash, pointer))

    if (credential_policy & CREDENTIAL_POLICY_FAIL_OR_WARN_UNUSUAL) != 0:
        props.append((None, "Path is unusual."))
    if (credential_policy & CREDENTIAL_POLICY_WARN_MISMATCH) != 0:
        props.append((None, "Credential doesn't match payment credential."))
    if (credential_policy & CREDENTIAL_POLICY_WARN_REWARD_ADDRESS) != 0:
        props.append(("Address is a reward address.", None))
    if (credential_policy & CREDENTIAL_POLICY_WARN_NO_STAKING) != 0:
        props.append(
            (
                "%s address - no staking rewards." % ADDRESS_TYPE_NAMES[address_type],
                None,
            )
        )

    if credential_policy >= CREDENTIAL_POLICY_WARN_SCRIPT:
        icon = ui.ICON_WRONG
        icon_color = ui.RED
    else:
        icon = ui.ICON_SEND
        icon_color = ui.GREEN

    if (credential_policy & CREDENTIAL_POLICY_SHOW_OUTPUT) != 0:
        title = "Confirm transaction"
    else:
        title = "%s address" % ADDRESS_TYPE_NAMES[address_type]

    await confirm_properties(
        ctx,
        "confirm_credential",
        title=title,
        props=props,
        icon=icon,
        icon_color=icon_color,
        br_code=ButtonRequestType.Other,
    )


async def show_warning_path(ctx: wire.Context, path: list[int], title: str) -> None:
    await confirm_path_warning(ctx, address_n_to_str(path), path_type=title)


async def show_warning_tx_output_contains_tokens(ctx: wire.Context) -> None:
    await confirm_metadata(
        ctx,
        "confirm_tokens",
        title="Confirm transaction",
        content="The following\ntransaction output\ncontains tokens.",
        larger_vspace=True,
        br_code=ButtonRequestType.Other,
    )


async def confirm_script_witness_request(
    ctx: wire.Context,
    script_witness_request: CardanoTxScriptWitnessRequest,
    signing_mode: CardanoTxSigningMode,
) -> None:
    assert (
        signing_mode == CardanoTxSigningMode.MULTISIG_TRANSACTION
    )  # _validate_script_witness_request

    await confirm_properties(
        ctx,
        "confirm_total",
        title="Confirm transaction",
        props=[
            (
                "Sign transaction with path:",
                address_n_to_str(script_witness_request.path),
            )
        ],
        br_code=ButtonRequestType.Other,
    )


async def confirm_transaction(
    ctx: wire.Context,
    fee: int,
    protocol_magic: int,
    ttl: int | None,
    validity_interval_start: int | None,
    is_network_id_verifiable: bool,
) -> None:
    props: list[PropertyType] = [
        ("Transaction fee:", format_coin_amount(fee)),
    ]

    if is_network_id_verifiable:
        props.append(
            ("Network: %s" % protocol_magics.to_ui_string(protocol_magic), None)
        )

    props.append(
        ("Valid since: %s" % format_optional_int(validity_interval_start), None)
    )
    props.append(("TTL: %s" % format_optional_int(ttl), None))

    await confirm_properties(
        ctx,
        "confirm_total",
        title="Confirm transaction",
        props=props,
        hold=True,
        br_code=ButtonRequestType.Other,
    )


async def confirm_certificate(
    ctx: wire.Context, certificate: CardanoTxCertificate
) -> None:
    # stake pool registration requires custom confirmation logic not covered
    # in this call
    assert certificate.type != CardanoCertificateType.STAKE_POOL_REGISTRATION

    props: list[PropertyType] = [
        ("Confirm:", CERTIFICATE_TYPE_NAMES[certificate.type]),
    ]

    if certificate.path:
        props.append(
            (
                "for account %s:" % format_account_number(certificate.path),
                address_n_to_str(to_account_path(certificate.path)),
            ),
        )
    else:
        assert certificate.script_hash is not None  # validate_certificate
        props.append(("for script:", format_script_hash(certificate.script_hash)))

    if certificate.type == CardanoCertificateType.STAKE_DELEGATION:
        assert certificate.pool is not None  # validate_certificate
        props.append(("to pool:", format_stake_pool_id(certificate.pool)))

    await confirm_properties(
        ctx,
        "confirm_certificate",
        title="Confirm transaction",
        props=props,
        br_code=ButtonRequestType.Other,
    )


async def confirm_stake_pool_parameters(
    ctx: wire.Context, pool_parameters: CardanoPoolParametersType
) -> None:
    margin_percentage = (
        100.0 * pool_parameters.margin_numerator / pool_parameters.margin_denominator
    )
    percentage_formatted = ("%f" % margin_percentage).rstrip("0").rstrip(".")
    await confirm_properties(
        ctx,
        "confirm_pool_registration",
        title="Confirm transaction",
        props=[
            (
                "Stake pool registration\nPool ID:",
                format_stake_pool_id(pool_parameters.pool_id),
            ),
            ("Pool reward account:", pool_parameters.reward_account),
            (
                "Pledge: {}\nCost: {}\nMargin: {}%".format(
                    format_coin_amount(pool_parameters.pledge),
                    format_coin_amount(pool_parameters.cost),
                    percentage_formatted,
                ),
                None,
            ),
        ],
        br_code=ButtonRequestType.Other,
    )


async def confirm_stake_pool_owner(
    ctx: wire.Context,
    keychain: seed.Keychain,
    owner: CardanoPoolOwner,
    protocol_magic: int,
    network_id: int,
) -> None:
    props: list[tuple[str, str | None]] = []
    if owner.staking_key_path:
        props.append(("Pool owner:", address_n_to_str(owner.staking_key_path)))
        props.append(
            (
                derive_human_readable_address(
                    keychain,
                    CardanoAddressParametersType(
                        address_type=CardanoAddressType.REWARD,
                        address_n=owner.staking_key_path,
                    ),
                    protocol_magic,
                    network_id,
                ),
                None,
            )
        )
    else:
        assert owner.staking_key_hash is not None  # validate_pool_owners
        props.append(
            (
                "Pool owner:",
                derive_human_readable_address(
                    keychain,
                    CardanoAddressParametersType(
                        address_type=CardanoAddressType.REWARD,
                        staking_key_hash=owner.staking_key_hash,
                    ),
                    protocol_magic,
                    network_id,
                ),
            )
        )

    await confirm_properties(
        ctx,
        "confirm_pool_owners",
        title="Confirm transaction",
        props=props,
        br_code=ButtonRequestType.Other,
    )


async def confirm_stake_pool_metadata(
    ctx: wire.Context,
    metadata: CardanoPoolMetadataType | None,
) -> None:
    if metadata is None:
        await confirm_properties(
            ctx,
            "confirm_pool_metadata",
            title="Confirm transaction",
            props=[("Pool has no metadata (anonymous pool)", None)],
            br_code=ButtonRequestType.Other,
        )
        return

    await confirm_properties(
        ctx,
        "confirm_pool_metadata",
        title="Confirm transaction",
        props=[
            ("Pool metadata url:", metadata.url),
            ("Pool metadata hash:", metadata.hash),
        ],
        br_code=ButtonRequestType.Other,
    )


async def confirm_stake_pool_registration_final(
    ctx: wire.Context,
    protocol_magic: int,
    ttl: int | None,
    validity_interval_start: int | None,
) -> None:
    await confirm_properties(
        ctx,
        "confirm_pool_final",
        title="Confirm transaction",
        props=[
            ("Confirm signing the stake pool registration as an owner\n\n\n", None),
            ("Network: %s" % protocol_magics.to_ui_string(protocol_magic), None),
            ("Valid since: %s" % format_optional_int(validity_interval_start), None),
            ("TTL: %s" % format_optional_int(ttl), None),
        ],
        hold=True,
        br_code=ButtonRequestType.Other,
    )


async def confirm_withdrawal(
    ctx: wire.Context, withdrawal: CardanoTxWithdrawal
) -> None:
    stake_credential_prop = (
        (
            "Confirm withdrawal\nfor account %s:"
            % format_account_number(withdrawal.path),
            address_n_to_str(to_account_path(withdrawal.path)),
        )
        if withdrawal.path
        else ("Confirm withdrawal for script:", withdrawal.script_hash)
    )
    await confirm_properties(
        ctx,
        "confirm_withdrawal",
        title="Confirm transaction",
        props=[
            stake_credential_prop,
            ("Amount:", format_coin_amount(withdrawal.amount)),
        ],
        br_code=ButtonRequestType.Other,
    )


async def confirm_catalyst_registration(
    ctx: wire.Context,
    public_key: str,
    staking_path: list[int],
    reward_address: str,
    nonce: int,
) -> None:
    await confirm_properties(
        ctx,
        "confirm_catalyst_registration",
        title="Confirm transaction",
        props=[
            ("Catalyst voting key registration", None),
            ("Voting public key:", public_key),
            (
                "Staking key for account %s:" % format_account_number(staking_path),
                address_n_to_str(staking_path),
            ),
            ("Rewards go to:", reward_address),
            ("Nonce:", str(nonce)),
        ],
        br_code=ButtonRequestType.Other,
    )


async def show_auxiliary_data_hash(
    ctx: wire.Context, auxiliary_data_hash: bytes
) -> None:
    await confirm_properties(
        ctx,
        "confirm_auxiliary_data",
        title="Confirm transaction",
        props=[("Auxiliary data hash:", auxiliary_data_hash)],
        br_code=ButtonRequestType.Other,
    )


async def show_warning_tx_contains_mint(ctx: wire.Context) -> None:
    await confirm_metadata(
        ctx,
        "confirm_tokens",
        title="Confirm transaction",
        content="The transaction contains\nminting or burning of\ntokens.",
        larger_vspace=True,
        br_code=ButtonRequestType.Other,
    )


async def confirm_token_minting(
    ctx: wire.Context, policy_id: bytes, token: CardanoToken
) -> None:
    assert token.mint_amount is not None  # _validate_token
    is_minting = token.mint_amount >= 0

    await confirm_properties(
        ctx,
        "confirm_mint",
        title="Confirm transaction",
        props=[
            (
                "Asset fingerprint:",
                format_asset_fingerprint(
                    policy_id=policy_id,
                    asset_name_bytes=token.asset_name_bytes,
                ),
            ),
            (
                "Amount %s:" % ("minted" if is_minting else "burnt"),
                format_amount(token.mint_amount, 0),
            ),
        ],
        br_code=ButtonRequestType.Other,
    )


async def show_warning_tx_network_unverifiable(ctx: wire.Context) -> None:
    await confirm_metadata(
        ctx,
        "warning_no_outputs",
        title="Warning",
        content="Transaction has no outputs, network cannot be verified.",
        larger_vspace=True,
        br_code=ButtonRequestType.Other,
    )


async def show_cardano_address(
    ctx: wire.Context,
    address_parameters: CardanoAddressParametersType,
    address: str,
    protocol_magic: int,
) -> None:
    network_name = None
    if not protocol_magics.is_mainnet(protocol_magic):
        network_name = protocol_magics.to_ui_string(protocol_magic)

    title = "%s address" % ADDRESS_TYPE_NAMES[address_parameters.address_type]
    address_extra = None
    title_qr = title
    if address_parameters.address_type in (
        CardanoAddressType.BYRON,
        CardanoAddressType.BASE,
        CardanoAddressType.BASE_KEY_SCRIPT,
        CardanoAddressType.POINTER,
        CardanoAddressType.ENTERPRISE,
        CardanoAddressType.REWARD,
    ):
        if address_parameters.address_n:
            address_extra = address_n_to_str(address_parameters.address_n)
            title_qr = address_n_to_str(address_parameters.address_n)
        elif address_parameters.address_n_staking:
            address_extra = address_n_to_str(address_parameters.address_n_staking)
            title_qr = address_n_to_str(address_parameters.address_n_staking)

    await show_address(
        ctx,
        address=address,
        title="%s address" % ADDRESS_TYPE_NAMES[address_parameters.address_type],
        network=network_name,
        address_extra=address_extra,
        title_qr=title_qr,
    )
