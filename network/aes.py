import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESHandler:
    """
    AES-256 GCM Encryption Handler
    """

    def __init__(self):
        pass

    @staticmethod
    def generate_key():
        """
        Generate a random 256-bit AES key.
        """

        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def encrypt(plaintext: str, key: bytes):

        aes = AESGCM(key)

        nonce = os.urandom(12)

        ciphertext = aes.encrypt(
            nonce,
            plaintext.encode(),
            None
        )

        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode()
        }

    @staticmethod
    def decrypt(ciphertext: str,
                nonce: str,
                key: bytes):

        aes = AESGCM(key)

        plaintext = aes.decrypt(
            base64.b64decode(nonce),
            base64.b64decode(ciphertext),
            None
        )

        return plaintext.decode()