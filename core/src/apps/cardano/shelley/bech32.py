from trezor.crypto import bech32


def bech32_encode(hr_part, b):
    convertedbits = bech32.convertbits(b, 8, 5)
    return bech32.bech32_encode(hr_part, convertedbits)


def bech32_decode(hrp, b):
    hrp_got, data = bech32.bech32_decode(b)
    if hrp_got != hrp:
        return (None, None)
    decoded = bech32.convertbits(data, 5, 8, False)
    return decoded
