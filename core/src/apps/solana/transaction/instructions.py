# generated from __init__.py.mako
# do not edit manually!
from typing import TYPE_CHECKING

from ..types import AccountTemplate, InstructionIdFormat, PropertyTemplate, UIProperty
from .instruction import Instruction

if TYPE_CHECKING:
    from typing import Any, Type, TypeGuard

    from ..types import Account

SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"

SYSTEM_PROGRAM_ID_INS_CREATE_ACCOUNT = 0


def __getattr__(name: str) -> Type[Instruction]:
    ids = {
        "SystemProgramCreateAccountInstruction": (
            "11111111111111111111111111111111",
            0,
        ),
    }
    id = ids[name]

    class FakeClass(Instruction):
        @classmethod
        def is_type_of(cls, ins: Any):
            return ins.program_id == id[0] and ins.instruction_id == id[1]

    return FakeClass


if TYPE_CHECKING:

    class SystemProgramCreateAccountInstruction(Instruction):
        PROGRAM_ID = SYSTEM_PROGRAM_ID
        INSTRUCTION_ID = SYSTEM_PROGRAM_ID_INS_CREATE_ACCOUNT

        lamports: int
        space: int
        owner: Account

        funding_account: Account
        new_account: Account

        @classmethod
        def is_type_of(
            cls, ins: Any
        ) -> TypeGuard["SystemProgramCreateAccountInstruction"]:
            return (
                ins.program_id == cls.PROGRAM_ID
                and ins.instruction_id == cls.INSTRUCTION_ID
            )


def get_instruction_id_length(program_id: str) -> InstructionIdFormat:
    if program_id == SYSTEM_PROGRAM_ID:
        return InstructionIdFormat(4, True)

    return InstructionIdFormat(0, False)


def get_instruction(
    program_id: str,
    instruction_id: int,
    instruction_accounts: list[Account],
    instruction_data: bytes,
) -> Instruction:
    if program_id == SYSTEM_PROGRAM_ID:
        if instruction_id == SYSTEM_PROGRAM_ID_INS_CREATE_ACCOUNT:
            return Instruction(
                instruction_data,
                program_id,
                instruction_accounts,
                SYSTEM_PROGRAM_ID_INS_CREATE_ACCOUNT,
                [
                    PropertyTemplate(
                        "lamports",
                        "u64",
                        False,
                    ),
                    PropertyTemplate(
                        "space",
                        "u64",
                        False,
                    ),
                    PropertyTemplate(
                        "owner",
                        "authority",
                        False,
                    ),
                ],
                [
                    AccountTemplate(
                        "funding_account",
                        False,
                    ),
                    AccountTemplate(
                        "new_account",
                        False,
                    ),
                ],
                [
                    UIProperty(
                        None,
                        "new_account",
                        "Create account",
                        None,
                        False,
                    ),
                    UIProperty(
                        "lamports",
                        None,
                        "Deposit",
                        "SOL",
                        False,
                    ),
                    UIProperty(
                        None,
                        "funding_account",
                        "From",
                        None,
                        True,
                    ),
                ],
                "System Program: Create Account",
                True,
                True,
                False,
                "Warning: Instruction is deprecated. Token decimals unknown.",
            )
        return Instruction(
            instruction_data,
            program_id,
            instruction_accounts,
            instruction_id,
            [],
            [],
            [],
            "System Program",
            True,
            False,
            False,
        )
    return Instruction(
        instruction_data,
        program_id,
        instruction_accounts,
        0,
        [],
        [],
        [],
        "Unsupported program",
        False,
        False,
        False,
    )
