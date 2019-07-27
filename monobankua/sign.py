from base64 import b64encode
from binascii import hexlify
from ecdsa import SigningKey
import hashlib


class SignKey:
    def __init__(self, private_key):
        self.private_key = private_key
        self.signing_key = SigningKey.from_pem(private_key)

    @property
    def key_id(self):
        public_key = self.signing_key.get_verifying_key()
        uncompressed_public_key = bytearray([0x04]) + (bytearray(public_key.to_string()))
        return hexlify(hashlib.sha1(uncompressed_public_key).digest())

    def sign(self, for_sign):
        sign = self.signing_key.sign(for_sign.encode(), hashfunc=hashlib.sha256)
        return b64encode(sign)
