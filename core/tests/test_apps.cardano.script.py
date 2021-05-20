from common import *
from trezor.crypto import bip32
from trezor.messages import CardanoScriptType
from trezor.messages.CardanoScript import CardanoScript

if not utils.BITCOIN_ONLY:
    from apps.cardano.seed import Keychain
    from apps.cardano.script import get_script_hash, validate_script


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoScript(unittest.TestCase):
    def test_get_script_hash(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        keychain = Keychain(node)

        # TODO GK add tests with key_path
        scripts = [
            # PUB_KEY
            [
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                    ),
                ),
                b"855228f5ecececf9c85618007cc3c2e5bdf5e6d41ef8d6fa793fe0eb",
            ],
            # ALL
            [
                CardanoScript(
                    type=CardanoScriptType.ALL,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "4a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                    ],
                ),
                b"13eac4f7f6576beb849b05f1be8ab52bc95057b48bf8aac1b09b6639",
            ],
            # ANY
            [
                CardanoScript(
                    type=CardanoScriptType.ANY,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "80f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa"
                            ),
                        ),
                    ],
                ),
                b"9cdfa95cd08e9876505423146a6f3fae9549e90e65280cfb08aba084",
            ],
            # N OF K
            [
                CardanoScript(
                    type=CardanoScriptType.N_OF_K,
                    required=2,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "4a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "5a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                    ],
                ),
                b"7fd4c8c1dd8548bde6c36264be97e89c2f33735277e541a25a1fc99f",
            ],
            # INVALID BEFORE
            [
                CardanoScript(
                    type=CardanoScriptType.ALL,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.INVALID_BEFORE, invalid_before=100
                        ),
                    ],
                ),
                b"e4599760db07340d8853cb3325823ead19cbafb7454b8b8b9afe0078",
            ],
            # INVALID HEREAFTER
            [
                CardanoScript(
                    type=CardanoScriptType.ALL,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.INVALID_HEREAFTER,
                            invalid_hereafter=200,
                        ),
                    ],
                ),
                b"cef4b6aa9b5ed7d10957b97e0eeebcf4cb3b3e99975d7239214d82f8",
            ],
            # NESTED SCRIPT
            [
                CardanoScript(
                    type=CardanoScriptType.ALL,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.ALL,
                            scripts=[
                                CardanoScript(
                                    type=CardanoScriptType.PUB_KEY,
                                    key_hash=unhexlify(
                                        "4a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                                    ),
                                ),
                            ],
                        ),
                        CardanoScript(
                            type=CardanoScriptType.INVALID_BEFORE, invalid_before=100
                        ),
                        CardanoScript(
                            type=CardanoScriptType.INVALID_HEREAFTER,
                            invalid_hereafter=200,
                        ),
                    ],
                ),
                b"0a510415456132b0342b48caa45e9618813efd374df901ae46790c11",
            ],
        ]

        for script, expected_hash in scripts:
            # TODO GK vectors could perhaps be taken out and validate_script could be a separate test function
            validate_script(script)

            actual_hash = get_script_hash(keychain, script)
            self.assertEqual(hexlify(actual_hash), expected_hash)


if __name__ == "__main__":
    unittest.main()
