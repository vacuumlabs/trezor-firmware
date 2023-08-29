# 01000103c80f8b50107e9f3e3c16a661b8c806df454a6deb293d5e8730a9d28f2f4998c68f41927b2e58cbc31ed3aa5163a7b8ca4eb5590e8dc1dc682426cd2895aa9c0a00000000000000000000000000000000000000000000000000000000000000001aea57c9906a7cad656ff61b3893abda63f4b6b210c939855e7ab6e54049213d01020200010c02000000002d310100000000
from typing import TYPE_CHECKING

from trezor.crypto import base58

from ..constants import (
    ADDRESS_READ_ONLY,
    ADDRESS_RW,
    ADDRESS_SIG,
    ADDRESS_SIG_READ_ONLY,
    ADDRESS_SIZE,
)
from .parse_instructions import parse_instructions
from .utils import read_compact_u16

if TYPE_CHECKING:
    from trezor.utils import BufferReader

    from ..types import Address, AddressReference, RawInstruction


def parse(
    serialized_tx: BufferReader,
) -> tuple[list[Address | AddressReference], bytes, list[RawInstruction]]:
    # TODO SOL: signature parsing can be removed?
    # num_of_signatures = decode_length(serialized_tx)
    # assert num_of_signatures == 0
    # signatures = []
    # for i in range(num_of_signatures):
    #     signature = serialized_tx.read(64)
    #     signatures.append(signature)

    is_v0 = False
    if serialized_tx.peek() & 0b10000000:
        serialized_tx.get()
        is_v0 = True

    (
        num_required_signatures,
        num_signature_read_only_addresses,
        num_read_only_addresses,
    ) = _parse_header(serialized_tx)

    addresses = _parse_addresses(
        serialized_tx,
        num_required_signatures,
        num_signature_read_only_addresses,
        num_read_only_addresses,
    )

    blockhash = bytes(serialized_tx.read(32))

    parsed_instructions = parse_instructions(serialized_tx)

    merged_addresses: list[Address | AddressReference] = []
    [merged_addresses.append(address) for address in addresses]
    if is_v0:
        (
            address_table_lookup_rw_addresses,
            address_table_lookup_ro_addresses,
        ) = _parse_lookup_tables(serialized_tx)

        for rw_address in address_table_lookup_rw_addresses:
            merged_addresses.append(rw_address)
        for ro_address in address_table_lookup_ro_addresses:
            merged_addresses.append(ro_address)

    # populate instructions with addresses or address references
    instructions = []
    for program_index, account_indexes, data in parsed_instructions:
        program_id = merged_addresses[program_index][0]
        instruction_accounts = []
        for index in account_indexes:
            instruction_accounts.append(merged_addresses[index])

        instructions.append((program_id, instruction_accounts, data))

    assert serialized_tx.remaining_count() == 0

    return merged_addresses, blockhash, instructions


def _parse_header(serialized_tx: BufferReader) -> tuple[int, int, int]:
    num_required_signatures = int.from_bytes(serialized_tx.read(1), "big")
    num_signature_read_only_addresses = int.from_bytes(serialized_tx.read(1), "big")
    num_read_only_addresses = int.from_bytes(serialized_tx.read(1), "big")

    return (
        num_required_signatures,
        num_signature_read_only_addresses,
        num_read_only_addresses,
    )


def _parse_addresses(
    serialized_tx: BufferReader,
    num_required_signatures: int,
    num_signature_read_only_addresses: int,
    num_read_only_addresses: int,
) -> list[Address]:
    num_of_addresses = read_compact_u16(serialized_tx)

    assert (
        num_of_addresses
        >= num_required_signatures
        + num_signature_read_only_addresses
        + num_read_only_addresses
    )

    addresses: list[Address] = []
    for i in range(num_of_addresses):
        assert ADDRESS_SIZE <= serialized_tx.remaining_count()

        address = serialized_tx.read(ADDRESS_SIZE)
        if i < num_required_signatures:
            type = ADDRESS_SIG
        elif i < num_required_signatures + num_signature_read_only_addresses:
            type = ADDRESS_SIG_READ_ONLY
        elif (
            i
            < num_required_signatures
            + num_signature_read_only_addresses
            + num_read_only_addresses
        ):
            type = ADDRESS_RW
        else:
            type = ADDRESS_READ_ONLY

        addresses.append((address, type))

    return addresses


def _parse_lookup_tables(serialized_tx: BufferReader):
    address_table_lookup_rw_addresses = []
    address_table_lookup_ro_addresses = []

    address_table_lookups_count = read_compact_u16(serialized_tx)
    for _ in range(address_table_lookups_count):
        account = base58.encode(serialized_tx.read(ADDRESS_SIZE))

        table_rw_indexes_count = read_compact_u16(serialized_tx)
        for _ in range(table_rw_indexes_count):
            address_table_lookup_rw_addresses.append(
                (account, serialized_tx.get(), ADDRESS_RW)
            )

        table_ro_indexes_count = read_compact_u16(serialized_tx)
        for _ in range(table_ro_indexes_count):
            address_table_lookup_ro_addresses.append(
                (account, serialized_tx.get(), ADDRESS_READ_ONLY)
            )

    return address_table_lookup_rw_addresses, address_table_lookup_ro_addresses
