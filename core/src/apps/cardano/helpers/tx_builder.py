from micropython import const

from trezor.crypto import hashlib

from apps.common import cbor

from .cbor_hash_builder import CborHashBuilder
from .lazy_cbor_collection import LazyCborDict, LazyCborList
from .tx_builder_state_machine import TxBuilderStateMachine

TX_BODY_KEY_INPUTS = const(0)
TX_BODY_KEY_OUTPUTS = const(1)
TX_BODY_KEY_FEE = const(2)
TX_BODY_KEY_TTL = const(3)
TX_BODY_KEY_CERTIFICATES = const(4)
TX_BODY_KEY_WITHDRAWALS = const(5)
TX_BODY_KEY_AUXILIARY_DATA = const(7)
TX_BODY_KEY_VALIDITY_INTERVAL_START = const(8)

POOL_REGISTRATION_CERTIFICATE_ITEMS_COUNT = 10


class TxBuilder:
    """
    Serves as a helper for interactions with cbor_hash_builder.
    """

    def __init__(self, tx_body_map_item_count: int):
        self.cbor_hash_builder = CborHashBuilder(
            hashlib.blake2b(outlen=32), LazyCborDict(tx_body_map_item_count)
        )
        self.state_machine = TxBuilderStateMachine()

    def get_tx_hash(self) -> bytes:
        assert self.state_machine.state == self.state_machine.STATE_END
        return self.cbor_hash_builder.get_hash()

    def start_inputs(self, inputs_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_INPUTS_START)
        self.cbor_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_INPUTS,
            collection=LazyCborList(inputs_count),
        )

    def add_input(self, prev_hash: bytes, prev_index: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_INPUT_ADD)
        self.cbor_hash_builder.add_item((prev_hash, prev_index))

    def finish_inputs(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_INPUTS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def start_outputs(self, outputs_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_OUTPUTS_START)
        self.cbor_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_OUTPUTS,
            collection=LazyCborList(outputs_count),
        )

    def add_simple_output(self, amount: int, address: bytes) -> None:
        self.state_machine.transition(
            TxBuilderStateMachine.ACTION_OUTPUT_ADD_WITHOUT_TOKENS
        )
        self.cbor_hash_builder.add_item((address, amount))

    def add_output_with_tokens(self, amount: int, address: bytes) -> None:
        self.state_machine.transition(
            TxBuilderStateMachine.ACTION_OUTPUT_ADD_WITH_TOKENS
        )
        # output structure is [address, [amount, asset_groups]]
        self.cbor_hash_builder.add_lazy_collection(LazyCborList(2))
        self.cbor_hash_builder.add_item(address)
        self.cbor_hash_builder.add_lazy_collection(LazyCborList(2))
        self.cbor_hash_builder.add_item(amount)

    def start_asset_groups(self, asset_groups_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_ASSET_GROUPS_START)
        self.cbor_hash_builder.add_lazy_collection(LazyCborDict(asset_groups_count))

    def add_asset_group(self, policy_id: bytes, tokens_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_ASSET_GROUP_ADD)
        self.cbor_hash_builder.add_lazy_collection_at_key(
            key=policy_id,
            collection=LazyCborDict(tokens_count),
        )

    def add_token(self, asset_name_bytes: bytes, amount: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_TOKEN_ADD)
        self.cbor_hash_builder.add_item((asset_name_bytes, amount))

    def finish_tokens(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_TOKENS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def finish_asset_groups(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_ASSET_GROUPS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def finish_output_with_tokens(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_OUTPUT_FINISH)
        # finish twice since an output with tokens contains a nested collection - [address, [amount, asset_groups]]
        self.cbor_hash_builder.finish_current_lazy_collection()
        self.cbor_hash_builder.finish_current_lazy_collection()

    def finish_outputs(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_OUTPUTS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def add_fee(self, fee: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_FEE_ADD)
        self.cbor_hash_builder.add_item((TX_BODY_KEY_FEE, fee))

    def add_ttl(self, ttl: int | None) -> None:
        if ttl is not None:
            self.state_machine.transition(TxBuilderStateMachine.ACTION_TTL_ADD)
            self.cbor_hash_builder.add_item((TX_BODY_KEY_TTL, ttl))

    def start_certificates(self, certificates_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_CERTIFICATES_START)
        self.cbor_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_CERTIFICATES,
            collection=LazyCborList(certificates_count),
        )

    def add_simple_certificate(
        self,
        cborized_certificate: cbor.CborSequence,
    ) -> None:
        self.state_machine.transition(
            TxBuilderStateMachine.ACTION_CERTIFICATE_ADD_SIMPLE
        )
        self.cbor_hash_builder.add_item(cborized_certificate)

    def start_pool_registration_certificate_and_add_fields(
        self,
        cborized_certificate_fields: cbor.CborSequence,
    ) -> None:
        """
        Adding a pool registration certificate is split up into multiple messages. That is why here we first add all
        the fields which come before pool_owners, then add pool_owners, pool_relays and finally pool_metadata in
        separate functions.
        """
        self.state_machine.transition(
            TxBuilderStateMachine.ACTION_CERTIFICATE_ADD_POOL_REGISTRATION
        )
        self.cbor_hash_builder.add_lazy_collection(
            LazyCborList(POOL_REGISTRATION_CERTIFICATE_ITEMS_COUNT)
        )
        for item in cborized_certificate_fields:
            self.cbor_hash_builder.add_item(item)

    def start_pool_owners(self, owners_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_OWNERS_START)
        self.cbor_hash_builder.add_lazy_collection(LazyCborList(owners_count))

    def add_pool_owner(self, cborized_pool_owner: bytes) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_OWNER_ADD)
        self.cbor_hash_builder.add_item(cborized_pool_owner)

    def finish_pool_owners(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_OWNERS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def start_pool_relays(self, relays_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_RELAYS_START)
        self.cbor_hash_builder.add_lazy_collection(LazyCborList(relays_count))

    def add_pool_relay(self, cborized_pool_relay: cbor.CborSequence) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_RELAY_ADD)
        self.cbor_hash_builder.add_item(cborized_pool_relay)

    def finish_pool_relays(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_RELAYS_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def add_pool_metadata(self, pool_metadata: cbor.CborSequence | None) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_POOL_METADATA_ADD)
        self.cbor_hash_builder.add_item(pool_metadata)

    def finish_pool_registration_certificate(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_CERTIFICATE_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def finish_certificates(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_CERTIFICATES_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def start_withdrawals(self, withdrawals_count: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_WITHDRAWALS_START)
        self.cbor_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_WITHDRAWALS,
            collection=LazyCborDict(withdrawals_count),
        )

    def add_withdrawal(self, reward_address: bytes, amount: int) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_WITHDRAWAL_ADD)
        self.cbor_hash_builder.add_item((reward_address, amount))

    def finish_withdrawals(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_WITHDRAWAL_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()

    def add_auxiliary_data_hash(self, auxiliary_data_hash: bytes) -> None:
        self.state_machine.transition(
            TxBuilderStateMachine.ACTION_AUXILIARY_DATA_HASH_ADD
        )
        self.cbor_hash_builder.add_item(
            (TX_BODY_KEY_AUXILIARY_DATA, auxiliary_data_hash)
        )

    def add_validity_interval_start(self, validity_interval_start: int | None) -> None:
        if validity_interval_start is not None:
            self.state_machine.transition(
                TxBuilderStateMachine.ACTION_VALIDITY_INTERVAL_START_ADD
            )
            self.cbor_hash_builder.add_item(
                (TX_BODY_KEY_VALIDITY_INTERVAL_START, validity_interval_start)
            )

    def finish(self) -> None:
        self.state_machine.transition(TxBuilderStateMachine.ACTION_FINISH)
        self.cbor_hash_builder.finish_current_lazy_collection()
