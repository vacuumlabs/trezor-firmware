from common import *
from trezor import wire
from trezor.crypto import bip32
from trezor.messages import CardanoScriptType
from trezor.messages.CardanoScript import CardanoScript

if not utils.BITCOIN_ONLY:
    from apps.cardano.seed import Keychain
    from apps.cardano.script import get_script_hash, validate_script

VALID_SCRIPTS = [
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
                    key_hash=unhexlify(
                        "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
            ],
        ),
        b"c991cd9b396abbed0cf63184ede0de8a96898c2a0ef84545b6ab9456",
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
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
            ],
        ),
        b"9019dcc82774961b56563fd709c34a72e33d3d18bce0cd5aebeac6ac",
    ],
    # N OF K
    [
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
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_hash=unhexlify(
                        "4a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
                    ),
                ),
                CardanoScript(
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
                ),
            ],
        ),
        b"b4864a4f22176a2a23259235ae581f2768f3e15a6ed53c5dc23a6dc8",
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
                    type=CardanoScriptType.PUB_KEY,
                    key_path=[1854 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0],
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
        b"77ed6cc234569d17fbf0d9c730fa31acb90f81f0fb8ae777836db1d8",
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
        scripts=CardanoScript(
            type=CardanoScriptType.PUB_KEY,
            key_hash=unhexlify(
                "3a55d9f68255dfbefa1efd711f82d005fae1be2e145d616c90cf0fa9"
            ),
        ),
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
