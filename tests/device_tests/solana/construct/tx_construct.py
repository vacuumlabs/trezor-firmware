import pytest

from trezorlib.debuglink import TrezorClientDebugLink as Client
from trezorlib.solana import sign_tx
from trezorlib.tools import parse_path

from tests.device_tests.solana.construct.templates import (
    CompactArray,
    PublicKey,
    Version,
    InstructionProgramId,
    Program,
)

from tests.device_tests.solana.construct.program_construct import (
    _SYSTEM_PROGRAM,
    _STAKE_PROGRAM,
    _COMPUTE_BUDGET_PROGRAM,
    _SYSTEM_PROGRAM_ACCOUNT,
)

from ....common import parametrize_using_common_fixtures

from construct import (
    ListContainer,
    Subconstruct,
    this,
    If,
    Construct,
    Container,
    Probe,
    Struct,
    Bytes,
    Array,
    Switch,
    Enum,
    Byte,
    Padding,
    PaddedString,
    Int8ul,
    Int32ul,
    Int32sl,
    Int64ul,
    Int64sl,
    stream_size,
    stream_seek,
)
from enum import IntEnum

from base58 import b58decode, b58encode

_HEADER = Struct(
    "signers" / Int8ul,
    "readonly_signers" / Int8ul,
    "readonly_non_signers" / Int8ul,
)

_ACCOUNTS = CompactArray(PublicKey())

_INSTRUCTION = Struct(
    "program_id" / InstructionProgramId(),
    "instruction_accounts" / _SYSTEM_PROGRAM_ACCOUNT,
    "data"
    / Switch(
        lambda this: this.program_id,
        {
            Program.SYSTEM_PROGRAM_ID: _SYSTEM_PROGRAM,
            Program.STAKE_PROGRAM_ID: _STAKE_PROGRAM,
            Program.COMPUTE_BUDGET_PROGRAM_ID: _COMPUTE_BUDGET_PROGRAM,
        },
        _SYSTEM_PROGRAM,
    ),
)


# TODO GK - luts
# _LUT = Struct(
#     "account" / _PUBLIC_KEY, "readwrite" / _ACCOUNT_IDXS, "readonly" / _ACCOUNT_IDXS
# )

# _LUTS = Struct("count" / CompactU16(), "items" / Array(this.count, _LUT))

_MESSAGE = Struct(
    "transaction" / Version(),
    "header" / _HEADER,
    "accounts" / _ACCOUNTS,
    "blockhash" / PublicKey(),
    "instructions" / CompactArray(_INSTRUCTION),
    # "luts" / If(this.transaction.versioned, _LUTS),
)
