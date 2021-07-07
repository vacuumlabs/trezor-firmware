import ustruct as struct
from micropython import const

from apps.common import cbor

if False:
    from typing import Generic, Iterator, Type, TypeVar

    T = TypeVar("T")
else:
    T = 0  # type: ignore
    Generic = [object]  # type: ignore


_CBOR_TYPE_ARRAY = const(0b100 << 5)
_CBOR_TYPE_MAP = const(0b101 << 5)


class LazyCborCollection(Generic[T]):
    """
    A base class for LazyCborCollections. Contains basic functionality for a lazy collection. Enables iteration over
    and CBOR serialization of its items as they are being added (one by one) thus never storing them all at once.
    """

    class PauseIteration:
        """
        Used to signal to consumers of LazyCborCollection that all available data has been consumed for now.
        """

        pass

    class EmptyElement:
        """
        Serves as a replacement for None since None can be a valid CBOR item.
        """

        pass

    def __init__(self, size: int) -> None:
        self.size = size
        self.added_elements_count = 0
        self.element: T | LazyCborCollection.EmptyElement = self.EmptyElement()

    def __len__(self) -> int:
        return self.size

    def is_filled(self) -> bool:
        return self.added_elements_count == self.size

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.is_filled() and isinstance(self.element, self.EmptyElement):
            raise StopIteration
        assert not isinstance(
            self.element, self.EmptyElement
        ), "The next element hasn't been added yet"
        element, self.element = self.element, self.EmptyElement()
        return element

    def append_item(self, item: T) -> None:
        assert isinstance(
            self.element, self.EmptyElement
        ), "The previous element hasn't been read yet"
        assert (
            self.added_elements_count < self.size
        ), "Item appended to a filled collection"
        self._validate_item(item)
        self.element = item
        self.added_elements_count += 1

    def _validate_item(self, item: T) -> None:
        pass

    def cbor_serialize(self) -> Iterator[bytes | Type[PauseIteration]]:
        """
        Provides a custom encoder to lazy collections which has the highest priority when being encoded into CBOR.
        This allows us to circumvent the default cbor serializer.
        """
        raise NotImplementedError


class LazyCborDict(LazyCborCollection):
    def _validate_item(self, item: tuple) -> None:
        assert len(item) == 2

    def cbor_serialize(
        self,
    ) -> Iterator[bytes | Type[LazyCborCollection.PauseIteration]]:
        yield _get_cbor_header(_CBOR_TYPE_MAP, self.size)
        yield self.PauseIteration

        for element in self:
            assert len(element) == 2
            key, value = element
            yield from cbor.encode_streamed(key)
            yield from cbor.encode_streamed(value)
            yield self.PauseIteration


class LazyCborList(LazyCborCollection):
    def cbor_serialize(
        self,
    ) -> Iterator[bytes | Type[LazyCborCollection.PauseIteration]]:
        yield _get_cbor_header(_CBOR_TYPE_ARRAY, self.size)
        yield self.PauseIteration

        for element in self:
            yield from cbor.encode_streamed(element)
            yield self.PauseIteration


def _get_cbor_header(typ: int, l: int) -> bytes:
    """
    Duplicate the cbor._header function so we don't have to expose it from cbor.py. This way the implementation details
    of cbor.py stay hidden and aren't exposed just for the sake of lazy collections.
    """
    if l < 24:
        return struct.pack(">B", typ + l)
    elif l < 2 ** 8:
        return struct.pack(">BB", typ + 24, l)
    elif l < 2 ** 16:
        return struct.pack(">BH", typ + 25, l)
    elif l < 2 ** 32:
        return struct.pack(">BI", typ + 26, l)
    elif l < 2 ** 64:
        return struct.pack(">BQ", typ + 27, l)
    else:
        raise NotImplementedError("Length %d not suppported" % l)
