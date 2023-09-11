# generated from program.py.mako
# do not edit manually!

from enum import IntEnum
import io
from construct import Int32ul, ListContainer, Probe, Struct, Subconstruct, Switch
from construct import (
    Construct,
    Int8ul,
    Int32ul,
    Int64ul,
    Padding,
    PaddedString,
    Struct,
    Switch,
    this,
)

from .templates import (
    AccountReference,
    CompactArray,
    CompactU16,
    InstructionProgramId,
    PublicKey,
)


# class AccountReference(Construct):
#     def _build(self, obj, stream, context, path):
#         account_index = context._._["accounts"].index(obj)
#         stream.write(account_index)
#         return obj


_STRING = Struct(
    "length" / Int8ul, Padding(4), "chars" / PaddedString(this.length, "utf-8")
)


class SystemProgramInstruction(IntEnum):
    INS_CREATE_ACCOUNT = 0
    INS_ASSIGN = 1
    INS_TRANSFER = 2
    INS_CREATE_ACCOUNT_WITH_SEED = 3
    INS_ALLOCATE = 8
    INS_ALLOCATE_WITH_SEED = 9
    INS_ASSIGN_WITH_SEED = 10


_SYSTEM_PROGRAM_ACCOUNT = Switch(
    lambda this: this.data["instruction_id"],
    {
        SystemProgramInstruction.INS_CREATE_ACCOUNT: Struct(
            "funding_account" / AccountReference(),
            "new_account" / AccountReference(),
        ),
        SystemProgramInstruction.INS_ASSIGN: Struct(
            "assigned_account" / AccountReference(),
        ),
        SystemProgramInstruction.INS_TRANSFER: Accounts(
            "funding_account" / AccountReference(),
            "recipient_account" / AccountReference(),
            Probe(),
        ),
        SystemProgramInstruction.INS_CREATE_ACCOUNT_WITH_SEED: Struct(
            "funding_account" / AccountReference(),
            "created_account" / AccountReference(),
            "base_account" / AccountReference(),
        ),
        SystemProgramInstruction.INS_ALLOCATE: Struct(
            "new_account" / AccountReference(),
        ),
        SystemProgramInstruction.INS_ALLOCATE_WITH_SEED: Struct(
            "allocated_account" / AccountReference(),
            "base_account" / AccountReference(),
        ),
        SystemProgramInstruction.INS_ASSIGN_WITH_SEED: Struct(
            "assigned_account" / AccountReference(),
            "base_account" / AccountReference(),
        ),
    },
)


_SYSTEM_PROGRAM = InstructionData(
    "instruction_id" / Int32ul,
    "parameters"
    / Switch(
        lambda this: this.instruction_id,
        {
            SystemProgramInstruction.INS_CREATE_ACCOUNT: Struct(
                "lamports" / Int64ul,
                "space" / Int64ul,
                "owner" / PublicKey(),
            ),
            SystemProgramInstruction.INS_ASSIGN: Struct(
                "owner" / PublicKey(),
            ),
            SystemProgramInstruction.INS_TRANSFER: Struct(
                "lamports" / Int64ul,
                Probe(),
            ),
            SystemProgramInstruction.INS_CREATE_ACCOUNT_WITH_SEED: Struct(
                "base" / PublicKey(),
                "seed" / _STRING,
                "lamports" / Int64ul,
                "space" / Int64ul,
                "owner" / PublicKey(),
            ),
            SystemProgramInstruction.INS_ALLOCATE: Struct(
                "space" / Int64ul,
            ),
            SystemProgramInstruction.INS_ALLOCATE_WITH_SEED: Struct(
                "base" / PublicKey(),
                "seed" / _STRING,
                "space" / Int64ul,
                "owner" / PublicKey(),
            ),
            SystemProgramInstruction.INS_ASSIGN_WITH_SEED: Struct(
                "base" / PublicKey(),
                "seed" / _STRING,
                "owner" / PublicKey(),
            ),
        },
    ),
    Probe(this),
)


class StakeProgramInstruction(IntEnum):
    INS_INITIALIZE = 0
    INS_AUTHORIZE = 1
    INS_DELEGATE_STAKE = 2
    INS_SPLIT = 3
    INS_WITHDRAW = 4
    INS_DEACTIVATE = 5
    INS_SET_LOCKUP = 6
    INS_MERGE = 7
    INS_AUTHORIZE_WITH_SEED = 8
    INS_INITIALIZE_CHECKED = 9
    INS_AUTHORIZE_CHECKED = 10
    INS_AUTHORIZE_CHECKED_WITH_SEED = 11
    INS_SET_LOCKUP_CHECKED = 12


_STAKE_PROGRAM = InstructionData(
    "instruction_id" / Int8ul,
    "instruction_accounts"
    / Switch(
        lambda this: this.instruction_id,
        {
            StakeProgramInstruction.INS_INITIALIZE: Struct(
                "uninitialized_stake_account" / AccountReference(),
                "rent_sysvar" / AccountReference(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE: Struct(
                "stake_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_or_withdraw_authority" / AccountReference(),
                "lockup_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_DELEGATE_STAKE: Struct(
                "initialized_stake_account" / AccountReference(),
                "vote_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_history_sysvar" / AccountReference(),
                "config_account" / AccountReference(),
                "stake_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_SPLIT: Struct(
                "stake_account" / AccountReference(),
                "uninitialized_stake_account" / AccountReference(),
                "stake_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_WITHDRAW: Struct(
                "stake_account" / AccountReference(),
                "recipient_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_history_sysvar" / AccountReference(),
                "withdraw_authority" / AccountReference(),
                "lockup_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_DEACTIVATE: Struct(
                "delegated_stake_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_SET_LOCKUP: Struct(
                "initialized_stake_account" / AccountReference(),
                "lockup_authority_or_withdraw_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_MERGE: Struct(
                "destination_stake_account" / AccountReference(),
                "source_stake_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_history_sysvar" / AccountReference(),
                "stake_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE_WITH_SEED: Struct(
                "stake_account" / AccountReference(),
                "stake_or_withdraw_authority" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "lockup_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_INITIALIZE_CHECKED: Struct(
                "uninitialized_stake_account" / AccountReference(),
                "rent_sysvar" / AccountReference(),
                "stake_authority" / AccountReference(),
                "withdraw_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE_CHECKED: Struct(
                "stake_account" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "stake_or_withdraw_authority" / AccountReference(),
                "new_stake_or_withdraw_authority" / AccountReference(),
                "lockup_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE_CHECKED_WITH_SEED: Struct(
                "stake_account" / AccountReference(),
                "stake_or_withdraw_authority" / AccountReference(),
                "clock_sysvar" / AccountReference(),
                "new_stake_or_withdraw_authority" / AccountReference(),
                "lockup_authority" / AccountReference(),
            ),
            StakeProgramInstruction.INS_SET_LOCKUP_CHECKED: Struct(
                "stake_account" / AccountReference(),
                "lockup_authority_or_withdraw_authority" / AccountReference(),
                "new_lockup_authority" / AccountReference(),
            ),
        },
    ),
    "parameters"
    / Switch(
        lambda this: this.instruction_id,
        {
            StakeProgramInstruction.INS_INITIALIZE: Struct(
                "staker" / PublicKey(),
                "withdrawer" / PublicKey(),
                "unix_timestamp" / Int64ul,
                "epoch" / Int64ul,
                "custodian" / PublicKey(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE: Struct(
                "pubkey" / PublicKey(),
                "stakeauthorize" / PublicKey(),
            ),
            StakeProgramInstruction.INS_DELEGATE_STAKE: Struct(),
            StakeProgramInstruction.INS_SPLIT: Struct(
                "lamports" / Int64ul,
            ),
            StakeProgramInstruction.INS_WITHDRAW: Struct(
                "lamports" / Int64ul,
            ),
            StakeProgramInstruction.INS_DEACTIVATE: Struct(),
            StakeProgramInstruction.INS_SET_LOCKUP: Struct(
                "unix_timestamp" / Int64ul,
                "epoch" / Int64ul,
                "custodian" / PublicKey(),
            ),
            StakeProgramInstruction.INS_MERGE: Struct(),
            StakeProgramInstruction.INS_AUTHORIZE_WITH_SEED: Struct(
                "new_authorized_pubkey" / PublicKey(),
                "stakeauthorize" / PublicKey(),
                "authority_seed" / _STRING,
                "authority_owner" / PublicKey(),
            ),
            StakeProgramInstruction.INS_INITIALIZE_CHECKED: Struct(),
            StakeProgramInstruction.INS_AUTHORIZE_CHECKED: Struct(
                "stakeauthorize" / PublicKey(),
            ),
            StakeProgramInstruction.INS_AUTHORIZE_CHECKED_WITH_SEED: Struct(
                "stakeauthorize" / PublicKey(),
                "authority_seed" / _STRING,
                "authority_owner" / PublicKey(),
            ),
            StakeProgramInstruction.INS_SET_LOCKUP_CHECKED: Struct(
                "unix_timestamp" / Int64ul,
                "epoch" / Int64ul,
            ),
        },
    ),
)


class ComputebudgetProgramInstruction(IntEnum):
    INS_REQUEST_HEAP_FRAME = 1
    INS_SET_COMPUTE_UNIT_LIMIT = 2
    INS_SET_COMPUTE_UNIT_PRICE = 3


_COMPUTE_BUDGET_PROGRAM = Struct(
    "instruction_id" / Int8ul,
    "instruction_accounts"
    / Switch(
        lambda this: this.instruction_id,
        {
            ComputebudgetProgramInstruction.INS_REQUEST_HEAP_FRAME: Struct(),
            ComputebudgetProgramInstruction.INS_SET_COMPUTE_UNIT_LIMIT: Struct(),
            ComputebudgetProgramInstruction.INS_SET_COMPUTE_UNIT_PRICE: Struct(),
        },
    ),
    "parameters"
    / Switch(
        lambda this: this.instruction_id,
        {
            ComputebudgetProgramInstruction.INS_REQUEST_HEAP_FRAME: Struct(
                "bytes" / Int32ul,
            ),
            ComputebudgetProgramInstruction.INS_SET_COMPUTE_UNIT_LIMIT: Struct(
                "units" / Int32ul,
            ),
            ComputebudgetProgramInstruction.INS_SET_COMPUTE_UNIT_PRICE: Struct(
                "lamports" / Int64ul,
            ),
        },
    ),
)
