from trezor.enums import CardanoAddressType

from ...common.paths import address_n_to_str
from .utils import format_key_hash, format_script_hash

if False:
    from trezor.messages import (
        CardanoBlockchainPointerType,
        CardanoAddressParametersType,
    )
    from trezor.ui.layouts import PropertyType


class CredentialParams:
    """
    Serves mainly as a wrapper object for credential parameters so that they don't have to be passed into functions
    separately. Also contains functions which simplify displaying the credential.
    """

    type: int
    address_type: CardanoAddressType
    path: list[int]
    key_hash: bytes | None
    script_hash: bytes | None
    pointer: CardanoBlockchainPointerType | None

    TYPE_PAYMENT = 0
    TYPE_STAKE = 1

    def __init__(self, type: int, address_parameters: CardanoAddressParametersType):
        self.type = type
        self.address_type = address_parameters.address_type

        if type == self.TYPE_PAYMENT:
            self.path = address_parameters.address_n
            self.key_hash = None
            self.script_hash = address_parameters.script_payment_hash
            self.pointer = None
        elif type == self.TYPE_STAKE:
            self.path = address_parameters.address_n_staking
            self.key_hash = address_parameters.staking_key_hash
            self.script_hash = address_parameters.script_staking_hash
            self.pointer = address_parameters.certificate_pointer
        else:
            raise ValueError

    def get_credential(self) -> list[int] | bytes | CardanoBlockchainPointerType | None:
        if self.path:
            return self.path
        elif self.key_hash:
            return self.key_hash
        elif self.script_hash:
            return self.script_hash
        elif self.pointer:
            return self.pointer
        else:
            return None

    def get_title(self) -> str:
        if self.path:
            return "path"
        elif self.key_hash:
            return "key hash"
        elif self.script_hash:
            return "script"
        elif self.pointer:
            return "pointer"
        else:
            return ""

    def format(self) -> list[PropertyType]:
        if self.path:
            return [(None, address_n_to_str(self.path))]
        elif self.key_hash:
            return [(None, format_key_hash(self.key_hash, False))]
        elif self.script_hash:
            return [(None, format_script_hash(self.script_hash))]
        elif self.pointer:
            return [
                ("Block: %s" % self.pointer.block_index, None),
                ("Transaction: %s" % self.pointer.tx_index, None),
                ("Certificate: %s" % self.pointer.certificate_index, None),
            ]
        else:
            return []

    def format_type(self) -> str:
        if self.type == self.TYPE_PAYMENT:
            return "payment"
        elif self.type == self.TYPE_STAKE:
            return "stake"

        raise ValueError
