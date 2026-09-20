"""
network/aes.py
--------------

AES-256-GCM authenticated encryption utilities.

Provides a lightweight wrapper around the official
cryptography AESGCM implementation.

Workflow
--------

32-byte AES Key
        │
        ▼
Generate Random 96-bit Nonce
        │
        ▼
AES-256-GCM
        │
        ▼
Ciphertext || Authentication Tag

Notes
-----
• AESGCM.encrypt() automatically appends the 16-byte
  authentication tag to the ciphertext.

• AESGCM.decrypt() automatically verifies the
  authentication tag before returning the plaintext.

• Any modification to the ciphertext, nonce, key,
  or authenticated data will cause decryption to fail.
"""

from __future__ import annotations

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AES256GCM:
    """
    AES-256-GCM helper.

    Parameters
    ----------
    key
        32-byte AES key.

    Notes
    -----
    • AES Key      : 256 bits (32 bytes)
    • Nonce        : 96 bits (12 bytes)
    • Auth Tag     : 128 bits (16 bytes)
    """

    KEY_SIZE = 32
    NONCE_SIZE = 12
    TAG_SIZE = 16

    def __init__(self, key: bytes) -> None:

        if not isinstance(key, bytes):
            raise TypeError("AES key must be bytes.")

        if len(key) != self.KEY_SIZE:
            raise ValueError(
                f"AES-256 requires exactly {self.KEY_SIZE} bytes."
            )

        self._key = key
        self._cipher = AESGCM(key)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def key(self) -> bytes:
        """
        Return the AES key.

        Mainly useful for debugging and testing.
        """
        return self._key

    # ------------------------------------------------------------------
    # Encryption
    # ------------------------------------------------------------------

    def encrypt(
        self,
        plaintext: bytes,
        associated_data: bytes | None = None,
    ) -> tuple[bytes, bytes]:
        """
        Encrypt plaintext using AES-256-GCM.

        Parameters
        ----------
        plaintext
            Raw bytes to encrypt.

        associated_data
            Optional Additional Authenticated Data (AAD).

        Returns
        -------
        tuple
            (nonce, ciphertext)

        Notes
        -----
        The returned ciphertext already includes the
        16-byte authentication tag.
        """

        if not isinstance(plaintext, bytes):
            raise TypeError(
                "Plaintext must be bytes."
            )

        nonce = os.urandom(self.NONCE_SIZE)

        ciphertext = self._cipher.encrypt(
            nonce,
            plaintext,
            associated_data,
        )

        return nonce, ciphertext

    # ------------------------------------------------------------------
    # Decryption
    # ------------------------------------------------------------------

    def decrypt(
        self,
        nonce: bytes,
        ciphertext: bytes,
        associated_data: bytes | None = None,
    ) -> bytes:
        """
        Decrypt ciphertext.

        Parameters
        ----------
        nonce
            12-byte AES-GCM nonce.

        ciphertext
            Ciphertext returned by encrypt().

        associated_data
            Same AAD supplied during encryption.

        Returns
        -------
        bytes
            Original plaintext.

        Raises
        ------
        ValueError
            Invalid nonce, empty ciphertext,
            or failed authentication.
        """

        if not isinstance(nonce, bytes):
            raise TypeError(
                "Nonce must be bytes."
            )

        if len(nonce) != self.NONCE_SIZE:
            raise ValueError(
                f"Nonce must be exactly {self.NONCE_SIZE} bytes."
            )

        if not isinstance(ciphertext, bytes):
            raise TypeError(
                "Ciphertext must be bytes."
            )

        if len(ciphertext) == 0:
            raise ValueError(
                "Ciphertext cannot be empty."
            )

        try:

            return self._cipher.decrypt(
                nonce,
                ciphertext,
                associated_data,
            )

        except InvalidTag as exc:

            raise ValueError(
                "AES-GCM authentication failed. "
                "Ciphertext may have been modified or corrupted."
            ) from exc

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a cryptographically secure
        256-bit AES key.

        Mostly useful for testing.

        HybridCrypto derives AES keys using HKDF,
        so this function is rarely needed in production.
        """

        return AESGCM.generate_key(
            bit_length=256
        )
    