"""
network/hybrid_crypto.py
------------------------

Hybrid Encryption Layer

Combines:

    ECDH (SECP256R1)
            │
            ▼
      Shared Secret
            │
            ▼
      HKDF-SHA256
            │
            ▼
      AES-256-GCM
            │
            ▼
    EncryptedPacket

Provides authenticated end-to-end encryption for telesurgery
messages before Garlic Routing.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .aes import AES256GCM
from .ecdh import ECDH
from .packet import EncryptedPacket


class HybridCrypto:
    """
    Hybrid Encryption using

    • ECDH
    • HKDF-SHA256
    • AES-256-GCM
    """

    AES_KEY_SIZE = 32

    HKDF_INFO = b"Telesurgery Hybrid Encryption"

    # ----------------------------------------------------------
    # HKDF
    # ----------------------------------------------------------

    @staticmethod
    def derive_key(
        shared_secret: bytes,
    ) -> bytes:
        """
        Derive a 256-bit AES key from the
        ECDH shared secret.
        """

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=HybridCrypto.AES_KEY_SIZE,
            salt=None,
            info=HybridCrypto.HKDF_INFO,
        )

        return hkdf.derive(shared_secret)

    # ----------------------------------------------------------
    # Encryption
    # ----------------------------------------------------------

    def encrypt(
        self,
        plaintext: bytes,
        receiver_public_key: bytes,
        workflow_id: str,
        sender: str,
        receiver: str,
        associated_data: bytes | None = None,
    ) -> EncryptedPacket:
        """
        Encrypt plaintext for a receiver.

        Parameters
        ----------
        plaintext
            Raw bytes.

        receiver_public_key
            Receiver public ECDH key.

        workflow_id
            Workflow identifier.

        sender
            Sending agent.

        receiver
            Receiving agent.

        associated_data
            Optional authenticated metadata.
        """

        sender_ecdh = ECDH()

        receiver_key = sender_ecdh.load_public_key(
            receiver_public_key
        )

        shared_secret = sender_ecdh.derive_shared_secret(
            receiver_key
        )

        aes_key = self.derive_key(
            shared_secret
        )

        cipher = AES256GCM(
            aes_key
        )

        nonce, ciphertext = cipher.encrypt(
            plaintext,
            associated_data,
        )

        return EncryptedPacket(

            workflow_id=workflow_id,

            sender=sender,

            receiver=receiver,

            sender_public_key=sender_ecdh.public_key_bytes(),

            nonce=nonce,

            ciphertext=ciphertext,
        )

    # ----------------------------------------------------------
    # Decryption
    # ----------------------------------------------------------

    def decrypt(
        self,
        packet: EncryptedPacket,
        receiver_ecdh: ECDH,
        associated_data: bytes | None = None,
    ) -> bytes:
        """
        Decrypt an EncryptedPacket.
        """

        sender_key = receiver_ecdh.load_public_key(
            packet.sender_public_key
        )

        shared_secret = receiver_ecdh.derive_shared_secret(
            sender_key
        )

        aes_key = self.derive_key(
            shared_secret
        )

        cipher = AES256GCM(
            aes_key
        )

        return cipher.decrypt(
            packet.nonce,
            packet.ciphertext,
            associated_data,
        )

    # ----------------------------------------------------------
    # Convenience
    # ----------------------------------------------------------

    @staticmethod
    def encrypt_text(
        text: str,
        receiver_public_key: bytes,
        workflow_id: str,
        sender: str,
        receiver: str,
    ) -> EncryptedPacket:
        """
        Encrypt a UTF-8 string.
        """

        crypto = HybridCrypto()

        return crypto.encrypt(
            plaintext=text.encode("utf-8"),
            receiver_public_key=receiver_public_key,
            workflow_id=workflow_id,
            sender=sender,
            receiver=receiver,
        )

    @staticmethod
    def decrypt_text(
        packet: EncryptedPacket,
        receiver_ecdh: ECDH,
    ) -> str:
        """
        Decrypt an EncryptedPacket into UTF-8 text.
        """

        crypto = HybridCrypto()

        plaintext = crypto.decrypt(
            packet,
            receiver_ecdh,
        )

        return plaintext.decode("utf-8")
    