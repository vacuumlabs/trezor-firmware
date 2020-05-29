from common import *
from trezor import wire
from trezor.crypto import bip32, slip39
from trezor.messages.CardanoCertificatePointerType import CardanoCertificatePointerType

from apps.common import HARDENED, seed

if not utils.BITCOIN_ONLY:
    from apps.cardano.seed import Keychain
    from apps.cardano.address import (
        validate_full_path,
        derive_base_address,
        derive_enterprise_address,
        derive_pointer_address,
        derive_bootstrap_address,
    )
    from apps.cardano.bootstrap_address import (
        _get_address_root,
        _address_hash,
        derive_address_and_node,
    )


@unittest.skipUnless(not utils.BITCOIN_ONLY, "altcoin")
class TestCardanoAddress(unittest.TestCase):
    def test_hardened_address_derivation_scheme(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        addresses = [
            "Ae2tdPwUPEZ98eHFwxSsPBDz73amioKpr58Vw85mP1tMkzq8siaftiejJ3j",
            "Ae2tdPwUPEZKA971NCHuHqaEnxZDFWPzH3fEsLpDnbEpG6UeMRHnRzCzEwK",
            "Ae2tdPwUPEZL9Ag1ouS4b1zjuPxKpvEUgjpVpG1KQFs5pNewQb65F1WXVQ2",
        ]

        for i, expected in enumerate(addresses):
            # 44'/1815'/0'/0/i'
            address, _ = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i + HARDENED])
            self.assertEqual(expected, address)

        nodes = [
            (
                b"3881a8de77d069001010d7f7d5211552e7d539b0e253add710367f95e528ed51",
                b"9b77608b38e0a0c7861aa234557c81482f42aae2d17993a8ddaec1868fb04d60",
                b"a938c8554ae04616cfaae7cd0eb557475082c4e910242ce774967e0bd7492408",
                b"cbf6ab47c8eb1a0477fc40b25dbb6c4a99454edb97d6fe5acedd3e238ef46fe0"
            ),
            (
                b"3003aca659846540b9ed04f2b844f2d8ea964856ca38a7dffedef4f6e528ed51",
                b"8844ccc81d633e1c7126f30c2524c1652617cf58da755014070215bf5070ba38",
                b"be28c00ed6cb9b70310f78028f8e3a2db935baf482d84afa590b0b5b864571cc",
                b"584b4631d752023a249e980779517280e6c0b3ac7a7f27c6e9456bfd228ca60b"
            ),
            (
                b"68e4482add0a741e14c8f2306bf83206a623e3729dd24175915eedece428ed51",
                b"3165a80c5efe846224d46a0427cdb2be4f31ea3585c51f4131faefc4328ad95a",
                b"9a32499976ffb582daa9988dfc42a303de5ed00c320c929f496be3c6eb1cf405",
                b"da07ca30a3d1c5fe3c34ce5fa197722446a646624a10bdf8889a4b9c347b2ef2"
            ),
        ]

        for i, (priv, ext, pub, chain) in enumerate(nodes):
            _, n = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i + HARDENED])
            self.assertEqual(hexlify(n.private_key()), priv)
            self.assertEqual(hexlify(n.private_key_ext()), ext)
            self.assertEqual(hexlify(seed.remove_ed25519_prefix(n.public_key())), pub)
            self.assertEqual(hexlify(n.chain_code()), chain)

    def test_non_hardened_address_derivation_scheme(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        addresses = [
            "Ae2tdPwUPEZ5YUb8sM3eS8JqKgrRLzhiu71crfuH2MFtqaYr5ACNRdsswsZ",
            "Ae2tdPwUPEZJb8r1VZxweSwHDTYtqeYqF39rZmVbrNK62JHd4Wd7Ytsc8eG",
            "Ae2tdPwUPEZFm6Y7aPZGKMyMAK16yA5pWWKU9g73ncUQNZsAjzjhszenCsq",
        ]

        for i, expected in enumerate(addresses):
            # 44'/1815'/0'/0/i
            address, _ = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i])
            self.assertEqual(address, expected)

        nodes = [
            (
                b"d03ba81163fd55af97bd132bf651a0da5b5e6201b15b1caca60b0be8e028ed51",
                b"493f44aa8d25fe0d3fe2935c76ea6b3e9e41c79e9dbcbe7131357c5aa1b6cac5",
                b"b90fb812a2268e9569ff1172e8daed1da3dc7e72c7bded7c5bcb7282039f90d5",
                b"fd8e71c1543de2cdc7f7623130c5f2cceb53549055fa1f5bc88199989e08cce7"
            ),
            (
                b"08b6438c8dd49d34b71c8e914d6ac3184e5ab3dcc8af023d08503a7edf28ed51",
                b"3fee605fdfaddc1ee2ea0b246b02c9abc54ad741054bc83943e8b21487b5a053",
                b"89053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea",
                b"26308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a635"
            ),
            (
                b"088f0275bf4a1bd18f08d7ef06c6ddb6ce7e3dc415fb4e89fe21bf39e628ed51",
                b"4c44563c7df519ea9b4d1801c1ab98b449db28b87f1c3837759c20f68c4c1e65",
                b"52548cb98e6f46a592bdf7f3598a9abc0126c78dfa3f46d1894ee52a5213e833",
                b"91af0668ee449e613e61bbb2482e5ddee1d9b15785727ec3e362c36861bff923"
            ),
        ]

        for i, (priv, ext, pub, chain) in enumerate(nodes):
            _, n = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i])
            self.assertEqual(hexlify(n.private_key()), priv)
            self.assertEqual(hexlify(n.private_key_ext()), ext)
            self.assertEqual(hexlify(seed.remove_ed25519_prefix(n.public_key())), pub)
            self.assertEqual(hexlify(n.chain_code()), chain)


    def test_root_address_derivation_scheme(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        # 44'/1815'
        address, _ = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED])
        self.assertEqual(address, "Ae2tdPwUPEZ2FGHX3yCKPSbSgyuuTYgMxNq652zKopxT4TuWvEd8Utd92w3")

        priv, ext, pub, chain = (
            b"204ec79cbb6502a141de60d274962010c7f1c94a2987b26506433184d228ed51",
            b"975cdd1c8610b44701567f05934c45c8716064263ccfe72ed2167ccb705c09b6",
            b"8c47ebce34234d04fd3dfbac33feaba6133e4e3d77c4b5ab18120ec6878ad4ce",
            b"02ac67c59a8b0264724a635774ca2c242afa10d7ab70e2bf0a8f7d4bb10f1f7a"
        )

        _, n = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED])
        self.assertEqual(hexlify(n.private_key()), priv)
        self.assertEqual(hexlify(n.private_key_ext()), ext)
        self.assertEqual(hexlify(seed.remove_ed25519_prefix(n.public_key())), pub)
        self.assertEqual(hexlify(n.chain_code()), chain)


    def test_address_hash(self):
        data = [0, [0, b"}\x1d\xe3\xf2/S\x90M\x00\x7f\xf83\xfa\xdd|\xd6H.\xa1\xe89\x18\xb9\x85\xb4\xea3\xe6<\x16\xd1\x83z\x04\xa6\xaa\xb0\xed\x12\xafV*&\xdbM\x104DT'M\x0b\xfan5\x81\xdf\x1d\xc0/\x13\xc5\xfb\xe5"], {}]
        result = _address_hash(data)

        self.assertEqual(result, b'\x1c\xca\xee\xc9\x80\xaf}\xb0\x9a\xa8\x96E\xd6\xa4\xd1\xb4\x13\x85\xb9\xc2q\x1d5/{\x12"\xca')


    def test_paths(self):
        incorrect_derivation_paths = [
            [44 | HARDENED],
            [44 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [43 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [44 | HARDENED, 1816 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [44 | HARDENED, 1815 | HARDENED, 0],
            [44 | HARDENED, 1815 | HARDENED, 0, 0],
            [44 | HARDENED, 1815 | HARDENED],
            [44 | HARDENED, 1815 | HARDENED, 0 | HARDENED],
            [44 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1, 1],
            [44 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 0, 0],  # a too large
            [1852 | HARDENED],
            [1852 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],            [43 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [1852 | HARDENED, 1816 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [1851 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1815 | HARDENED],
            [1852 | HARDENED, 1815 | HARDENED, 0],
            [1852 | HARDENED, 1815 | HARDENED, 0, 0],
            [1852 | HARDENED, 1815 | HARDENED],
            [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED],
            [1852 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 1, 1],
            [1852 | HARDENED, 1815 | HARDENED, 1815 | HARDENED, 0, 0],  # a too large
        ]
        correct_derivation_paths = [
            [44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 1],
            [44 | HARDENED, 1815 | HARDENED, 9 | HARDENED, 0, 4],
            [44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 9],
            [44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 1, 1],
            [44 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 1, 9],
            [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 1],
            [1852 | HARDENED, 1815 | HARDENED, 9 | HARDENED, 0, 4],
            [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 9],
            [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 1, 1],
            [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 1, 9],
        ]

        for path in incorrect_derivation_paths:
            self.assertFalse(validate_full_path(path))

        for path in correct_derivation_paths:
            self.assertTrue(validate_full_path(path))

    def test_get_address_root_scheme(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        root_node = bip32.from_mnemonic_cardano(mnemonic, passphrase)

        address_root = _get_address_root(root_node, {1: b'X\x1cr,zu\x81?\xaf\xde\x9f\xf9\xe4\xd4\x90\xadH$\xe9\xf3\x88\x16\xcb\xd2)\x02M\x0c#\xde'})
        self.assertEqual(address_root, b'\xb3\xbbS\xa8;uN:E=\xe8\xe5\x9c\x18\xbcn\xcf\xd0c\xba\x0e\xba\xaelL}\xba\xbb')

    def test_slip39_128(self):
        mnemonics = [
            "extra extend academic bishop cricket bundle tofu goat apart victim "
                "enlarge program behavior permit course armed jerky faint language modern",
            "extra extend academic acne away best indicate impact square oasis "
                "prospect painting voting guest either argue username racism enemy eclipse",
            "extra extend academic arcade born dive legal hush gross briefing "
                "talent drug much home firefly toxic analysis idea umbrella slice"
        ]
        passphrase = b"TREZOR"
        identifier, exponent, ems = slip39.recover_ems(mnemonics)
        master_secret = slip39.decrypt(ems, passphrase, exponent, identifier)

        node = bip32.from_seed(master_secret, "ed25519 cardano seed")

        # Check root node.
        root_priv = b"c0fe4a6973df4de06262693fc9186f71faf292960350882d49456bf108d13954"
        root_ext = b"4064253ffefc4127489bce1b825a47329010c5afb4d21154ef949ef786204405"
        root_pub = b"83e3ecaf57f90f022c45e10d1b8cb78499c30819515ad9a81ad82139fdb12a90"
        root_chain = b"22c12755afdd192742613b3062069390743ea232bc1b366c8f41e37292af9305"

        self.assertEqual(hexlify(node.private_key()), root_priv)
        self.assertEqual(hexlify(node.private_key_ext()), root_ext)
        self.assertEqual(hexlify(seed.remove_ed25519_prefix(node.public_key())), root_pub)
        self.assertEqual(hexlify(node.chain_code()), root_chain)

        # Check derived nodes and addresses.
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        nodes = [
            (
                "Ae2tdPwUPEYxF9NAMNdd3v2LZoMeWp7gCZiDb6bZzFQeeVASzoP7HC4V9s6",
                b"e0acfe234aa6e1219ce7d3d8d91853e0808bab92ecb8a0ff0f345ff31ad13954",
                b"ff89dc71365c4b67bb7bb75d566e65b8a95f16e4d70cce51c25937db15614530",
                b"bc043d84b8b891d49890edb6aced6f2d78395f255c5b6aea8878b913f83e8579",
                b"dc3f0d2b5cccb822335ef6213fd133f4ca934151ec44a6000aee43b8a101078c",
            ),
            (
                "Ae2tdPwUPEZ1TjYcvfkWAbiHtGVxv4byEHHZoSyQXjPJ362DifCe1ykgqgy",
                b"d0ce3e7a6445bc91801319b9bbaf47fdfca9364257295fb13bc5046a20d13954",
                b"c800359abdc875944754ae7368bab7ef75184d48816c368f5a28af4bcf1d1ee8",
                b"24c4fe188a39103db88818bc191fd8571eae7b284ebcbdf2462bde97b058a95c",
                b"6f7a744035f4b3ddb8f861c18446169643cc3ae85e271b4b4f0eda05cf84c65b",
            ),
            (
                "Ae2tdPwUPEZGXmSbda1kBNfyhRQGRcQxJFdk7mhWZXAGnapyejv2b2U3aRb",
                b"e8320644cce22a6e9fc33865fc5a598b1cda061c47a548aead3af4ed1cd13954",
                b"9e2ece5d7fe8119cb76090009be926a84fc5d3b95855b5962ffe2f880836cf09",
                b"831a63d381a8dab1e6e1ee991a4300fc70687aae5f97f4fcf92ed1b6c2bd99de",
                b"672d6af4707aba201b7940231e83dd357f92f8851b3dfdc224ef311e1b64cdeb"
            )
        ]

        for i, (address, priv, ext, pub, chain) in enumerate(nodes):
            # 44'/1815'/0'/0/i
            a, n = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i])
            self.assertEqual(a, address)
            self.assertEqual(hexlify(n.private_key()), priv)
            self.assertEqual(hexlify(n.private_key_ext()), ext)
            self.assertEqual(hexlify(seed.remove_ed25519_prefix(n.public_key())), pub)
            self.assertEqual(hexlify(n.chain_code()), chain)

    def test_slip39_256(self):
        mnemonics = [
            "hobo romp academic axis august founder knife legal recover alien expect "
                "emphasis loan kitchen involve teacher capture rebuild trial numb spider forward "
                "ladle lying voter typical security quantity hawk legs idle leaves gasoline",
            "hobo romp academic agency ancestor industry argue sister scene midst graduate "
                "profile numb paid headset airport daisy flame express scene usual welcome "
                "quick silent downtown oral critical step remove says rhythm venture aunt"
        ]
        passphrase = b"TREZOR"
        identifier, exponent, ems = slip39.recover_ems(mnemonics)
        master_secret = slip39.decrypt(ems, passphrase, exponent, identifier)

        node = bip32.from_seed(master_secret, "ed25519 cardano seed")

        # Check root node.
        root_priv = b"90633724b5daf770a8b420b8658e7d8bc21e066b60ec8cd4d5730681cc294e4f"
        root_ext = b"f9d99bf3cd9c7e12663e8646afa40cb3aecf15d91f2abc15d21056c6bccb3414"
        root_pub = b"eea170f0ef97b59d22907cb429888029721ed67d3e7a1b56b81731086ab7db64"
        root_chain = b"04f1de750b62725fcc1ae1b93ca4063acb53c486b959cadaa100ebd7828e5460"

        self.assertEqual(hexlify(node.private_key()), root_priv)
        self.assertEqual(hexlify(node.private_key_ext()), root_ext)
        self.assertEqual(hexlify(seed.remove_ed25519_prefix(node.public_key())), root_pub)
        self.assertEqual(hexlify(node.chain_code()), root_chain)

        # Check derived nodes and addresses.
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        nodes = [
            (
                "Ae2tdPwUPEYyDD1C2FbVJFAE3FuAxLspfMYt29TJ1urnSKr57cVhEcioSCC",
                b"38e8a4b17ca07b6a309f1cee83f87593e34a1fc3a289785ea451ef65df294e4f",
                b"405d10ef71c2b0019250d11837de8db825d8556bf1e57f8866920af6d8c90002",
                b"967a9a041ad1379e31c2c7f2aa4bc2b3f7769341c0ea89ccfb12a904f2e10877",
                b"7b15d8d9006afe3cd7e04f375a1126a8c7c7c07c59a6f0c5b0310f4245f4edbb",
            ),
            (
                "Ae2tdPwUPEZHJGtyz47F6wD7qAegt1JNRJWuiE36QLvFzeqJPBZ2EBvhr8M",
                b"a09f90e3f76a7bdb7f8721cc0c142dbd6398fd704b83455e123fa886dc294e4f",
                b"917e4166bb404def9f12634e84ecbcb98afdea051ba7c38745e208178a9e9baf",
                b"6f3805bbc1b7a75afa95dffec331671f3c4662800615e80d2ec1202a9d874c86",
                b"44baf30fd549e6a1e05f99c2a2c8971aea8894ee8d9c5fc2c5ae6ee839a56b2d",
            ),
            (
                "Ae2tdPwUPEYxD9xNPBJTzYmtFVVWEPB6KW4TCDijQ4pDwU11wt5621PyCi4",
                b"78dd824aea33bed5c1502d1a17f11a4adbe923aac1cd1f7ae98c9506db294e4f",
                b"ddfe7f27e2894b983df773d8ac2a07973fc37ff36e93a2f2d71fb7327d4e18f4",
                b"7f145b50ef07fb9accc40ee07a01fe93ceb6fa07d5a9f20fc3c8a48246dd4d02",
                b"e67d2864614ada5eec8fb8ee1225a94a6fb0a1b3c347c854ec3037351c6a0fc7",
            )
        ]

        for i, (address, priv, ext, pub, chain) in enumerate(nodes):
            # 44'/1815'/0'/0/i
            a, n = derive_address_and_node(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i])
            self.assertEqual(a, address)
            self.assertEqual(hexlify(n.private_key()), priv)
            self.assertEqual(hexlify(n.private_key_ext()), ext)
            self.assertEqual(hexlify(seed.remove_ed25519_prefix(n.public_key())), pub)
            self.assertEqual(hexlify(n.chain_code()), chain)

    def test_base_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(1852 | HARDENED)
        node.derive_cardano(1815 | HARDENED)

        keychain = Keychain([1852 | HARDENED, 1815 | HARDENED], node)

        test_vectors = [
            # network id, account, expected result
            # data from shelley test vectors
            (0, 0, "addr1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqcyl47r"),
            (3, 0, "addr1qw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqzhyupd"),
            # data generated with code under test
            (0, 4, "addr1qr4sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgmcs5wgus8qt4atk45lvt4xfxpjtwfhdmvchdf2m3u3hlsuzz8x7"),
            (3, 4, "addr1q04sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgmcs5wgus8qt4atk45lvt4xfxpjtwfhdmvchdf2m3u3hlsx3ewes"),
        ]

        for network_id, account, expected_address in test_vectors:
            actual_address = derive_base_address(keychain, [1852 | HARDENED, 1815 | HARDENED, account | HARDENED, 0, 0], network_id, None)

            self.assertEqual(actual_address, expected_address)


    def test_base_address_with_staking_key_hash(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(1852 | HARDENED)
        node.derive_cardano(1815 | HARDENED)

        keychain = Keychain([1852 | HARDENED, 1815 | HARDENED], node)

        test_vectors = [
            # network id, account, staking key hash, expected result
            # own staking key hash
            # data from shelley test vectors
            (0, 0, unhexlify("32c728d3861e164cab28cb8f006448139c8f1740ffb8e7aa9e5232dc"), "addr1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqcyl47r"),
            (3, 0, unhexlify("32c728d3861e164cab28cb8f006448139c8f1740ffb8e7aa9e5232dc"), "addr1qw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqzhyupd"),
            # data generated with code under test
            (0, 4, unhexlify("1bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff"), "addr1qr4sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgmcs5wgus8qt4atk45lvt4xfxpjtwfhdmvchdf2m3u3hlsuzz8x7"),
            (3, 4, unhexlify("1bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff"), "addr1q04sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgmcs5wgus8qt4atk45lvt4xfxpjtwfhdmvchdf2m3u3hlsx3ewes"),
            # staking key hash not owned - derived with "all all..." mnenomnic, data generated with code under test
            (0, 4, unhexlify("122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277"), "addr1qr4sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgj922xhxkn6twlq2wn4q50q352annk3903tj00h45mgfmsh42t2h"),
            (3, 0, unhexlify("122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277"), "addr1qw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzersj922xhxkn6twlq2wn4q50q352annk3903tj00h45mgfms3rqaac"),
            (3, 4, unhexlify("122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277"), "addr1q04sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgj922xhxkn6twlq2wn4q50q352annk3903tj00h45mgfmsdx3z4e"),
        ]

        for network_id, account, staking_key_hash, expected_address in test_vectors:
            actual_address = derive_base_address(keychain, [1852 | HARDENED, 1815 | HARDENED, account | HARDENED, 0, 0], network_id, staking_key_hash)
            self.assertEqual(actual_address, expected_address)

    def test_enterprise_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(1852 | HARDENED)
        node.derive_cardano(1815 | HARDENED)

        keychain = Keychain([1852 | HARDENED, 1815 | HARDENED], node)

        test_vectors = [
            # network id, expected result
            (0, "addr1vz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6g8jlq"),
            (3, "addr1vw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers6h7glf")
        ]

        for network_id, expected_address in test_vectors:
            actual_address = derive_enterprise_address(keychain, [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0], network_id)
            self.assertEqual(actual_address, expected_address)

    def test_pointer_address(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(1852 | HARDENED)
        node.derive_cardano(1815 | HARDENED)

        keychain = Keychain([1852 | HARDENED, 1815 | HARDENED], node)

        test_vectors = [
            # network id, pointer, expected result
            (0, CardanoCertificatePointerType(1, 2, 3), "addr1gz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerspqgpslhplej"),
            (3, CardanoCertificatePointerType(24157, 177, 42), "addr1gw2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5ph3wczvf2x4v58t")
        ]

        for network_id, pointer, expected_address in test_vectors:
            actual_address = derive_pointer_address(keychain, [1852 | HARDENED, 1815 | HARDENED, 0 | HARDENED, 0, 0], network_id, pointer)
            self.assertEqual(actual_address, expected_address)


    def test_shelley_address_with_byron_namespace(self):
        mnemonic = "test walk nut penalty hip pave soap entry language right filter choice"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)

        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        with self.assertRaises(wire.DataError):
            derive_base_address(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, 0], 0, None)

        with self.assertRaises(wire.DataError):
            derive_pointer_address(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, 0], 0, CardanoCertificatePointerType(0, 0, 0))

        with self.assertRaises(wire.DataError):
            derive_enterprise_address(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, 0], 0)


    def test_bootstrap_address(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(44 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([44 | HARDENED, 1815 | HARDENED], node)

        addresses = [
            "Ae2tdPwUPEZ5YUb8sM3eS8JqKgrRLzhiu71crfuH2MFtqaYr5ACNRdsswsZ",
            "Ae2tdPwUPEZJb8r1VZxweSwHDTYtqeYqF39rZmVbrNK62JHd4Wd7Ytsc8eG",
            "Ae2tdPwUPEZFm6Y7aPZGKMyMAK16yA5pWWKU9g73ncUQNZsAjzjhszenCsq",
        ]

        for i, expected_address in enumerate(addresses):
            # 44'/1815'/0'/0/i
            actual_address = derive_bootstrap_address(keychain, [44 | HARDENED, 1815 | HARDENED, HARDENED, 0, i])

            self.assertEqual(actual_address, expected_address)

    def test_bootstrap_with_shelley_namespace(self):
        mnemonic = "all all all all all all all all all all all all"
        passphrase = ""
        node = bip32.from_mnemonic_cardano(mnemonic, passphrase)
        node.derive_cardano(1852 | HARDENED)
        node.derive_cardano(1815 | HARDENED)
        keychain = Keychain([1852 | HARDENED, 1815 | HARDENED], node)

        with self.assertRaises(wire.DataError):
            derive_bootstrap_address(keychain, [1852 | HARDENED, 1815 | HARDENED, HARDENED, 0, 0])


if __name__ == '__main__':
    unittest.main()
