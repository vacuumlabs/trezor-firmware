# generated from __init__.py.mako
# do not edit manually!

from enum import IntEnum

from construct import (
    Byte,
    GreedyBytes,
    GreedyRange,
    Int32ul,
    Int64ul,
    Optional,
    Struct,
    Switch,
)

from .custom_constructs import (
    CompactArray,
    CompactStruct,
    HexStringAdapter,
    InstructionIdAdapter,
    Memo,
    PublicKey,
    String,
)


class Program:
    SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"


INSTRUCTION_ID_FORMATS = {
    Program.SYSTEM_PROGRAM_ID: {"length": 4, "is_included_if_zero": True},
}


# System Program begin


class SystemProgramInstruction(IntEnum):
    INS_CREATE_ACCOUNT = 0


SystemProgram_CreateAccount_Instruction = Struct(
    "program_index" / Byte,
    "accounts"
    / CompactStruct(
        "funding_account" / Byte,
        "new_account" / Byte,
    ),
    "data"
    / CompactStruct(
        "instruction_id" / InstructionIdAdapter(GreedyBytes),
        "lamports" / Int64ul,
        "space" / Int64ul,
        "owner" / PublicKey,
    ),
)


SystemProgram_Instruction = Switch(
    lambda this: this.instruction_id,
    {
        SystemProgramInstruction.INS_CREATE_ACCOUNT: SystemProgram_CreateAccount_Instruction,
    },
)

# System Program end

Instruction = Switch(
    lambda this: this.program_id,
    {
        Program.SYSTEM_PROGRAM_ID: SystemProgram_Instruction,
    },
    # unknown instruction
    Struct(
        "program_index" / Byte,
        "accounts" / CompactArray(Byte),
        "data" / HexStringAdapter(GreedyBytes),
    ),
)
