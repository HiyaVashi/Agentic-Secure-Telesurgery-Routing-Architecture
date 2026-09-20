from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class ECCHandler:
    """
    ECC (ECDH) Key Exchange Handler
    """

    @staticmethod
    def generate_key_pair():
        """
        Generate an ECC private/public key pair.
        """

        private_key = ec.generate_private_key(
            ec.SECP256R1()
        )

        public_key = private_key.public_key()

        return private_key, public_key

    @staticmethod
    def serialize_public_key(public_key):
        """
        Convert public key to bytes.
        """

        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def load_public_key(public_bytes):
        """
        Load a public key from bytes.
        """

        return serialization.load_pem_public_key(
            public_bytes
        )

    @staticmethod
    def derive_shared_key(private_key, peer_public_key):
        """
        Generate a shared secret using ECDH.
        """

        shared_secret = private_key.exchange(
            ec.ECDH(),
            peer_public_key
        )

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,           # 32 bytes = AES-256 key
            salt=None,
            info=b"Telesurgery Secure Channel"
        ).derive(shared_secret)

        return derived_key