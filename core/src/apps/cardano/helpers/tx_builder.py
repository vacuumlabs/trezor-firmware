from micropython import const

from trezor.crypto import hashlib
from trezor.enums import CardanoCertificateType

from apps.cardano.helpers.cbor_hash_builder import CborHashBuilder
from apps.cardano.helpers.lazy_cbor_collection import LazyCborDict, LazyCborList

TX_BODY_KEY_INPUTS = const(0)
TX_BODY_KEY_OUTPUTS = const(1)
TX_BODY_KEY_FEE = const(2)
TX_BODY_KEY_TTL = const(3)
TX_BODY_KEY_CERTIFICATES = const(4)
TX_BODY_KEY_WITHDRAWALS = const(5)
TX_BODY_KEY_AUXILIARY_DATA = const(7)
TX_BODY_KEY_VALIDITY_INTERVAL_START = const(8)

POOL_REGISTRATION_CERTIFICATE_ITEMS_COUNT = 10

if False:
    from typing import Any, Callable, Iterator, Union

    Generator = Iterator[
        Union[
            Callable[[int], None],
            Callable[[CardanoCertificateType], None],
            Callable[[tuple], None],
            Callable[[bytes], None],
            None,
        ]
    ]


class TxBuilder:
    def __init__(
        self,
        inputs_count: int,
        outputs_count: int,
        fee: int,
        ttl: int | None,
        certificates_count: int,
        withdrawals_count: int,
        has_auxiliary_data: bool,
        validity_interval_start: int | None,
    ):
        self._inputs_count = inputs_count
        self._outputs_count = outputs_count
        self._fee = fee
        self._ttl = ttl
        self._certificates_count = certificates_count
        self._withdrawals_count = withdrawals_count
        self._has_auxiliary_data = has_auxiliary_data
        self._validity_interval_start = validity_interval_start

        self._current_asset_groups_count: int | None = None
        self._current_policy_id: bytes | None = None
        self._current_token_count: int | None = None
        self._current_certificate_type: CardanoCertificateType | None = None
        self._current_initial_pool_registration_items: tuple | None = None
        self._current_pool_owners_count: int | None = None
        self._current_relays_count: int | None = None
        self._auxiliary_data_hash: bytes | None = None

        # inputs, outputs and fee are mandatory fields, count the number of optional fields present
        tx_body_map_item_count = 3 + sum(
            (
                self._ttl is not None,
                self._certificates_count > 0,
                self._withdrawals_count > 0,
                self._has_auxiliary_data,
                self._validity_interval_start is not None,
            )
        )
        self._tx_hash_builder = CborHashBuilder(
            hashlib.blake2b(outlen=32), LazyCborDict(tx_body_map_item_count)
        )

        self.generator = self._create_generator()

    def _create_generator(
        self,
    ) -> Generator:
        # inputs
        self._tx_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_INPUTS,
            collection=LazyCborList(self._inputs_count),
        )
        for _ in range(self._inputs_count):
            yield self._tx_hash_builder.add_item
        self._tx_hash_builder.finish_current_lazy_collection()

        # outputs
        self._tx_hash_builder.add_lazy_collection_at_key(
            key=TX_BODY_KEY_OUTPUTS,
            collection=LazyCborList(self._outputs_count),
        )
        for _ in range(self._outputs_count):
            # get asset groups count
            yield self._set_current_asset_groups_count
            if self._current_asset_groups_count is None:
                raise ValueError

            asset_groups_count = self._current_asset_groups_count
            if asset_groups_count == 0:
                # simple output
                yield self._tx_hash_builder.add_item
            else:
                # output
                self._tx_hash_builder.add_lazy_collection(LazyCborList(2))
                yield self._tx_hash_builder.add_item
                # output value
                self._tx_hash_builder.add_lazy_collection(LazyCborList(2))
                yield self._tx_hash_builder.add_item
                # asset groups
                self._tx_hash_builder.add_lazy_collection(
                    LazyCborDict(asset_groups_count)
                )
                for _ in range(asset_groups_count):
                    yield self._set_current_policy_id
                    if self._current_policy_id is None:
                        raise ValueError

                    yield self._set_current_token_count
                    if self._current_token_count is None:
                        raise ValueError

                    self._tx_hash_builder.add_lazy_collection_at_key(
                        key=self._current_policy_id,
                        collection=LazyCborDict(self._current_token_count),
                    )
                    # tokens
                    for _ in range(self._current_token_count):
                        yield self._tx_hash_builder.add_item
                    self._tx_hash_builder.finish_current_lazy_collection()

                    self._current_policy_id = None
                    self._current_token_count = None

                # asset groups
                self._tx_hash_builder.finish_current_lazy_collection()
                # output value
                self._tx_hash_builder.finish_current_lazy_collection()
                # output
                self._tx_hash_builder.finish_current_lazy_collection()

            self._current_asset_groups_count = None

        self._tx_hash_builder.finish_current_lazy_collection()

        # fee
        self._tx_hash_builder.add_item((TX_BODY_KEY_FEE, self._fee))

        # ttl
        if self._ttl is not None:
            self._tx_hash_builder.add_item((TX_BODY_KEY_TTL, self._ttl))

        # certificates
        if self._certificates_count > 0:
            self._tx_hash_builder.add_lazy_collection_at_key(
                key=TX_BODY_KEY_CERTIFICATES,
                collection=LazyCborList(self._certificates_count),
            )
            for _ in range(self._certificates_count):
                yield self._set_current_certificate_type
                if self._current_certificate_type is None:
                    raise ValueError

                if (
                    self._current_certificate_type
                    == CardanoCertificateType.STAKE_POOL_REGISTRATION
                ):
                    self._tx_hash_builder.add_lazy_collection(
                        LazyCborList(POOL_REGISTRATION_CERTIFICATE_ITEMS_COUNT)
                    )

                    # initial items
                    yield self._set_current_initial_pool_registration_items
                    if (
                        self._current_initial_pool_registration_items is None
                        or not isinstance(
                            self._current_initial_pool_registration_items, tuple
                        )
                        or len(self._current_initial_pool_registration_items) != 7
                    ):
                        raise ValueError

                    initial_items = self._current_initial_pool_registration_items

                    for item in initial_items:
                        self._tx_hash_builder.add_item(item)

                    # owners
                    yield self._set_current_pool_owners_count
                    if self._current_pool_owners_count is None:
                        raise ValueError

                    self._tx_hash_builder.add_lazy_collection(
                        LazyCborList(self._current_pool_owners_count)
                    )
                    for _ in range(self._current_pool_owners_count):
                        yield self._tx_hash_builder.add_item
                    self._tx_hash_builder.finish_current_lazy_collection()

                    # relays
                    yield self._set_current_relays_count
                    if self._current_relays_count is None:
                        raise ValueError

                    self._tx_hash_builder.add_lazy_collection(
                        LazyCborList(self._current_relays_count)
                    )
                    for _ in range(self._current_relays_count):
                        yield self._tx_hash_builder.add_item
                    self._tx_hash_builder.finish_current_lazy_collection()

                    # metadata
                    yield self._tx_hash_builder.add_item

                    self._tx_hash_builder.finish_current_lazy_collection()

                    self._current_certificate_type = None
                    self._current_initial_pool_registration_items = None
                    self._current_pool_owners_count = None
                    self._current_relays_count = None
                else:
                    yield self._tx_hash_builder.add_item
            self._tx_hash_builder.finish_current_lazy_collection()

        # withdrawals
        if self._withdrawals_count > 0:
            self._tx_hash_builder.add_lazy_collection_at_key(
                key=TX_BODY_KEY_WITHDRAWALS,
                collection=LazyCborDict(self._withdrawals_count),
            )
            for _ in range(self._withdrawals_count):
                yield self._tx_hash_builder.add_item
            self._tx_hash_builder.finish_current_lazy_collection()

        # auxiliary data
        if self._has_auxiliary_data:
            yield self._set_auxiliary_data_hash
            if self._auxiliary_data_hash is None:
                raise ValueError

            self._tx_hash_builder.add_item(
                (TX_BODY_KEY_AUXILIARY_DATA, self._auxiliary_data_hash)
            )
            self._auxiliary_data_hash = None

        # ttl
        if self._validity_interval_start is not None:
            self._tx_hash_builder.add_item(
                (TX_BODY_KEY_VALIDITY_INTERVAL_START, self._validity_interval_start)
            )

        self._tx_hash_builder.finish_current_lazy_collection()

        yield None

    def _set_current_asset_groups_count(self, asset_groups_count: int) -> None:
        self._current_asset_groups_count = asset_groups_count

    def _set_current_policy_id(self, policy_id: bytes) -> None:
        self._current_policy_id = policy_id

    def _set_current_token_count(self, token_count: int) -> None:
        self._current_token_count = token_count

    def _set_current_certificate_type(
        self, certificate_type: CardanoCertificateType
    ) -> None:
        self._current_certificate_type = certificate_type

    def _set_current_pool_owners_count(self, owners_count: int) -> None:
        self._current_pool_owners_count = owners_count

    def _set_current_relays_count(self, relays: int) -> None:
        self._current_relays_count = relays

    def _set_current_initial_pool_registration_items(
        self, initial_pool_registration_items: tuple
    ) -> None:
        self._current_initial_pool_registration_items = initial_pool_registration_items

    def _set_auxiliary_data_hash(self, auxiliary_data_hash: bytes) -> None:
        self._auxiliary_data_hash = auxiliary_data_hash

    def send(self, item: Any) -> None:
        fn = next(self.generator)
        if fn:
            fn(item)

    def finish(self) -> None:
        next(self.generator)

    def get_tx_hash(self) -> bytes:
        return self._tx_hash_builder.get_hash()
