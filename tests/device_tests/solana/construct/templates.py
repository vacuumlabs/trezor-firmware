import io
import pytest

from trezorlib.debuglink import TrezorClientDebugLink as Client
from trezorlib.solana import sign_tx
from trezorlib.tools import parse_path

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
from enum import Enum

from base58 import b58decode, b58encode


def _find_in_context(context, key):
    if key in context:
        return context[key]
    elif context._ is not None:
        return _find_in_context(context._, key)
    else:
        return None


class Version(Construct):
    def _build(self, obj, stream, context, path):
        if obj["versioned"]:
            stream.write(bytes([obj.version | 0x80]))

        return obj


class CompactU16(Construct):
    def _build(self, obj, stream, context, path):
        value = obj
        while True:
            B = value & 0x7F
            value >>= 7
            if value == 0:
                stream.write(bytes([B]))
                break

            stream.write(bytes([B | 0x80]))

        return obj


class PublicKey(Construct):
    def _build(self, obj, stream, context, path):
        stream.write(b58decode(obj))
        return obj


class CompactArray(Subconstruct):
    def _build(self, obj, stream, context, path):
        CompactU16()._build(len(obj), stream, context, path)

        retlist = ListContainer()
        for i, e in enumerate(obj):
            context._index = i
            retlist.append(self.subcon._build(e, stream, context, path))

        return retlist


class InstructionProgramId(Construct):
    def _build(self, obj, stream, context, path):
        program_index = context._["accounts"].index(obj)
        stream.write(bytes([program_index]))
        return obj


class Accounts(Struct):
    def _build(self, obj, stream, context, path):
        CompactU16()._build(len(obj), stream, context, path)
        super()._build(obj, stream, context, path)
        return obj


class InstructionData(Struct):
    def _build(self, obj, stream, context, path):
        size_stream = io.BytesIO()
        super()._build(obj, size_stream, context, path)
        size = len(size_stream.getvalue())

        CompactU16()._build(size, stream, context, path)
        super()._build(obj, stream, context, path)

        return obj


class AccountReference(Construct):
    def _build(self, obj, stream, context, path):
        accounts = _find_in_context(context, "accounts")
        account_index = accounts.index(obj)

        stream.write(bytes([account_index]))

        return obj


class Program(Enum):
    SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"
    STAKE_PROGRAM_ID = "Stake11111111111111111111111111111111111111"
    COMPUTE_BUDGET_PROGRAM_ID = "ComputeBudget111111111111111111111111111111"


_PUBLIC_KEY = PublicKey()

_HEADER = Struct(
    "signers" / Int8ul,
    "readonly_signers" / Int8ul,
    "readonly_non_signers" / Int8ul,
)

_ACCOUNTS = CompactArray(PublicKey())

_STRING = Struct(
    "length" / Int32ul, Padding(4), "chars" / PaddedString(this.length, "utf-8")
)
