from common import *
from apps.common import seed

from apps.common import HARDENED
from trezor.crypto import bip32, slip39
if not utils.BITCOIN_ONLY:
    from apps.cardano.shelley.address import (
        get_base_address,
        get_enterprise_address,
        get_pointer_address,
    )
    from apps.cardano.shelley.seed import Keychain


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoAddress(unittest.TestCase):
    def test_base_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(0x80000000 | 1852)
        node.derive_cardano(0x80000000 | 1815)

        keychain = Keychain([0x80000000 | 1852, 0x80000000 | 1815], node)

        test_vectors = [
            # network id, expected result
            (0, "addr1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqcyl47r"),
            (3, "addr1qw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqzhyupd")
        ]

        for expected in test_vectors:
            expected_address = expected[1]

            actual_address = get_base_address(keychain, [0x80000000 | 1852, 0x80000000 | 1815, 0x80000000 | 0, 0, 0], expected[0])

            self.assertEqual(actual_address, expected_address)
    

    def test_enterprise_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(0x80000000 | 1852)
        node.derive_cardano(0x80000000 | 1815)

        keychain = Keychain([0x80000000 | 1852, 0x80000000 | 1815], node)

        test_vectors = [
            # network id, expected result
            (0, "addr1vz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6g8jlq"),
            (3, "addr1vw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6h7glf")
        ]        

        for expected in test_vectors:
            expected_address = expected[1]

            actual_address = get_enterprise_address(keychain, [0x80000000 | 1852, 0x80000000 | 1815, 0x80000000 | 0, 0, 0], expected[0])

            self.assertEqual(actual_address, expected_address)
    

    def test_pointer_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(0x80000000 | 1852)
        node.derive_cardano(0x80000000 | 1815)

        keychain = Keychain([0x80000000 | 1852, 0x80000000 | 1815], node)

        test_vectors = [
            # network id, block_index, tx_index, certificate_index, expected result
            (0, 1, 2, 3, "addr1gz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerspqgpslhplej"),
            (3, 24157, 177, 42, "addr1gw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5ph3wczvf2x4v58t")
        ]

        for expected in test_vectors:
            expected_address = expected[4]
            
            actual_address = get_pointer_address(keychain, [0x80000000 | 1852, 0x80000000 | 1815, 0x80000000 | 0, 0, 0], expected[0], expected[1], expected[2], expected[3])

            self.assertEqual(actual_address, expected_address)


if __name__ == '__main__':
    unittest.main()
