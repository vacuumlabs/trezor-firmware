from common import *
from trezor import wire
from trezor.crypto import bip32
from trezor.enums import CardanoScriptType
from trezor.messages import CardanoScript

if not utils.BITCOIN_ONLY:
    from apps.cardano.seed import Keychain
    from apps.cardano.script import get_script_hash, validate_script

VALID_SCRIPTS = [
    # PUB_KEY
    [
        CardanoScript(
            type=CardanoScriptType.PUB_KEY,
            key_hash=unhexlify(
                "c4b9265645fde9536c0795adbcc5291767a0c61fd62448341d7e0386"
            ),
        ),
        b"29fb5fd4aa8cadd6705acc8263cee0fc62edca5ac38db593fec2f9fd",
    ],
    # PUB_KEY with path
    [
        CardanoScript(
            type=CardanoScriptType.PUB_KEY,
            key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
        ),
        b"29fb5fd4aa8cadd6705acc8263cee0fc62edca5ac38db593fec2f9fd",
    ],
    # ALL
    [
        CardanoScript(
            type=CardanoScriptType.ALL,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "0241f2d196f52a92fbd2183d03b370c30b6960cfdeae364ffabac889"
                    ),
                ),
            ],
        ),
        b"af5c2ce476a6ede1c879f7b1909d6a0b96cb2081391712d4a355cef6",
    ],
    # ANY
    [
        CardanoScript(
            type=CardanoScriptType.ANY,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "0241f2d196f52a92fbd2183d03b370c30b6960cfdeae364ffabac889"
                    ),
                ),
            ],
        ),
        b"d6428ec36719146b7b5fb3a2d5322ce702d32762b8c7eeeb797a20db",
    ],
    # N OF K
    [
        CardanoScript(
            type=CardanoScriptType.N_OF_K,
            required_signatures_count=2,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "0241f2d196f52a92fbd2183d03b370c30b6960cfdeae364ffabac889"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "cecb1d427c4ae436d28cc0f8ae9bb37501a5b77bcc64cd1693e9ae20"
                    ),
                ),
            ],
        ),
        b"2b2b17fd18e18acae4601d4818a1dee00a917ff72e772fa8482e36c9",
    ],
    # INVALID BEFORE
    [
        CardanoScript(
            type=CardanoScriptType.ALL,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "c4b9265645fde9536c0795adbcc5291767a0c61fd62448341d7e0386"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.INVALID_BEFORE, invalid_before=100
                ),
            ],
        ),
        b"c6262ef9bb2b1291c058d93b46dabf458e2d135f803f60713f84b0b7",
    ],
    # INVALID HEREAFTER
    [
        CardanoScript(
            type=CardanoScriptType.ALL,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "c4b9265645fde9536c0795adbcc5291767a0c61fd62448341d7e0386"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.INVALID_HEREAFTER,
                    invalid_hereafter=200,
                ),
            ],
        ),
        b"b12ac304f89f4cd4d23f59a2b90d2b2697f7540b8f470d6aa05851b5",
    ],
    # NESTED SCRIPT
    [
        CardanoScript(
            type=CardanoScriptType.ALL,
            scripts=[
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "c4b9265645fde9536c0795adbcc5291767a0c61fd62448341d7e0386"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
                CardanoScript(
                    type=CardanoScriptType.ANY,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "0241f2d196f52a92fbd2183d03b370c30b6960cfdeae364ffabac889"
                            ),
                        ),
                    ],
                ),
                CardanoScript(
                    type=CardanoScriptType.N_OF_K,
                    required_signatures_count=2,
                    scripts=[
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "0241f2d196f52a92fbd2183d03b370c30b6960cfdeae364ffabac889"
                            ),
                        ),
                        CardanoScript(
                            type=CardanoScriptType.PUB_KEY,
                            key_hash=unhexlify(
                                "cecb1d427c4ae436d28cc0f8ae9bb37501a5b77bcc64cd1693e9ae20"
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
        b"4a6b4288459bf34668c0b281f922691460caf0c7c09caee3a726c27a",
    ],
]

INVALID_SCRIPTS = [
    # PUB_KEY key_hash has invalid length
    CardanoScript(
        type=CardanoScriptType.PUB_KEY,
        key_hash=unhexlify("3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0f"),
    ),
    # PUB_KEY key_path is not multisig
    CardanoScript(
        type=CardanoScriptType.PUB_KEY,
        key_path=[1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
    ),
    # ALL scripts are empty
    CardanoScript(type=CardanoScriptType.ALL, scripts=[]),
    # ALL scripts are not set
    CardanoScript(type=CardanoScriptType.ALL, scripts=None),
    # ANY scripts are empty
    CardanoScript(type=CardanoScriptType.ANY, scripts=[]),
    # ANY scripts are not set
    CardanoScript(type=CardanoScriptType.ANY, scripts=None),
    # N_OF_K scripts are empty
    CardanoScript(
        type=CardanoScriptType.N_OF_K, required_signatures_count=2, scripts=[]
    ),
    # N_OF_K scripts are not set
    CardanoScript(
        type=CardanoScriptType.N_OF_K, required_signatures_count=2, scripts=None
    ),
    # N_OF_K required_signatures_count is not set
    CardanoScript(
        type=CardanoScriptType.N_OF_K,
        scripts=[
            CardanoScript(
                type=CardanoScriptType.PUB_KEY,
                key_hash=unhexlify(
                    "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                ),
            ),
        ],
    ),
    # N_OF_K N is larger than K
    CardanoScript(
        type=CardanoScriptType.N_OF_K,
        required_signatures_count=2,
        scripts=[
            CardanoScript(
                type=CardanoScriptType.PUB_KEY,
                key_hash=unhexlify(
                    "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                ),
            ),
        ],
    ),
    # INVALID_BEFORE invalid_before is not set
    CardanoScript(type=CardanoScriptType.INVALID_BEFORE),
    # INVALID_HEREAFTER invalid_hereafter is not set
    CardanoScript(type=CardanoScriptType.INVALID_HEREAFTER),
]


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoScript(unittest.TestCase):
    def test_get_script_hash(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        keychain = Keychain(node)

        for script, expected_hash in VALID_SCRIPTS:
            actual_hash = get_script_hash(keychain, script)
            self.assertEqual(hexlify(actual_hash), expected_hash)

    def test_validate_script(self):
        for script, _ in VALID_SCRIPTS:
            validate_script(script)

    def test_validate_script_invalid(self):
        for script in INVALID_SCRIPTS:
            with self.assertRaises(wire.ProcessError):
                validate_script(script)


if __name__ == "__main__":
    unittest.main()
