from apps.cardano.helpers.lazy_cbor_collection import (
    LazyCborCollection,
    LazyCborDict,
    LazyCborList,
)

if False:
    from typing import Any
    from trezor.utils import HashContext


class CborHashBuilder:
    """
    Builds a transaction hash in a streamed, lazy manner by keeping a stack of LazyCollections which get progressively
    filled up with items.
    """

    def __init__(self, hash_fn: HashContext, initial_active_item: LazyCborCollection):
        self.hash_fn = hash_fn
        self.active_items_stack: list[LazyCborCollection] = [initial_active_item]
        self.serializer = initial_active_item.cbor_serialize()

        self._update_hash()

    def _update_hash(self) -> None:
        while (chunk := next(self.serializer)) is not LazyCborCollection.PauseIteration:
            # for type checking
            assert isinstance(chunk, bytes)
            self.hash_fn.update(chunk)

    def get_hash(self) -> bytes:
        assert (
            len(self.active_items_stack) == 0
        ), "The hash calculation is not finished yet"

        return self.hash_fn.digest()

    def add_lazy_collection(self, collection: LazyCborCollection) -> None:
        """
        Add lazy collection to the collection at the top of the stack and then add it to the stack itself.
        The collection at the top of the stack must be a LazyCborList.
        """
        assert isinstance(self.active_items_stack[-1], LazyCborList)
        self.add_item(collection)
        self.active_items_stack.append(collection)

    def add_lazy_collection_at_key(
        self,
        key: Any,
        collection: LazyCborCollection,
    ) -> None:
        """
        Add lazy collection paired with a key to the collection at the top of the stack and then add it to
        the stack itself. The collection at the top of the stack must be a LazyCborDict.
        """
        assert isinstance(self.active_items_stack[-1], LazyCborDict)
        self.add_item((key, collection))
        self.active_items_stack.append(collection)

    def add_item(
        self,
        item: Any,
    ) -> None:
        """
        Add item to the collection at the top of the stack.
        """
        assert len(self.active_items_stack) > 0
        self.active_items_stack[-1].append_item(item)
        self._update_hash()

    def finish_current_lazy_collection(self) -> None:
        assert len(self.active_items_stack) > 0
        collection = self.active_items_stack.pop()
        assert collection.is_filled(), "The collection is not filled yet"
        if len(self.active_items_stack) == 0:
            # this was the last collection in the stack, no more PauseIteration left to consume
            return

        # consume closing PauseIteration yielded from the parent collection after consuming this item
        remaining_pause_iteration_item = next(self.serializer)
        assert remaining_pause_iteration_item is LazyCborCollection.PauseIteration
