import rsa

# https://cloud.tencent.com/developer/article/1751336
class RsaEncrypt:
    def __init__(self, e, m):
        self.e = e
        self.m = m

    def encrypt(self, message):
        mm = int(self.m, 16)
        ee = int(self.e, 16)
        rsa_pubkey = rsa.PublicKey(mm, ee)
        crypto = self._encrypt(message.encode(), rsa_pubkey)
        return crypto.hex()

    def _pad_for_encryption(self, message, target_length):
        message = message[::-1]
        max_msglength = target_length - 11
        msglength = len(message)

        padding = b''
        padding_length = target_length - msglength - 3

        for i in range(padding_length):
            padding += b'\x00'

        return b''.join([b'\x00\x00', padding, b'\x00', message])

    def _encrypt(self, message, pub_key):
        keylength = rsa.common.byte_size(pub_key.n)
        padded = self._pad_for_encryption(message, keylength)

        payload = rsa.transform.bytes2int(padded)
        encrypted = rsa.core.encrypt_int(payload, pub_key.e, pub_key.n)
        block = rsa.transform.int2bytes(encrypted, keylength)

        return block

def encode_password(password: str):
    en = RsaEncrypt("010001", "008c147f73c2593cba0bd007e60a89ade5")
    return en.encrypt(password)
import base64

def base64_encode(msg):
    return base64.b64encode(msg.encode()).decode()

def base64_decode(msg):
    return base64.b64decode(msg.encode()).decode()
