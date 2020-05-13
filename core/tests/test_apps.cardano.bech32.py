from common import *

from apps.cardano.shelley.bech32 import bech32_encode, bech32_decode


# todo: GK - other tests? Encode, Decode separately
@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoBech32(unittest.TestCase):
    def test_decode_and_encode(self):
        valid_bechs = [
            # human readable part, bech32
            ("a", "a12uel5l"),
            ("an83characterlonghumanreadablepartthatcontainsthenumber1andtheexcludedcharactersbio",
                "an83characterlonghumanreadablepartthatcontainsthenumber1andtheexcludedcharactersbio1tt5tgs"),
            ("abcdef", "abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw"),
            ("1", "11qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqc8247j"),
            ("split", "split1checkupstagehandshakeupstreamerranterredcaperred2y9e3w"),
        ]

        for valid_bech_tuple in valid_bechs:
            valid_hrp = valid_bech_tuple[0]
            valid_bech = valid_bech_tuple[1]

            decoded = bech32_decode(valid_hrp, valid_bech)
            encoded = bech32_encode(valid_hrp, decoded)

            self.assertEqual(encoded, valid_bech)


if __name__ == '__main__':
    unittest.main()
