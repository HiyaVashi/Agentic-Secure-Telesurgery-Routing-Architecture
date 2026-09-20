
"""
network/ecdh.py
----------------

Elliptic Curve Diffie-Hellman (ECDH) utilities.

Implements ephemeral key exchange using the NIST P-256 curve
(SECP256R1) to establish a shared secret between two peers.

Workflow
--------
Sender
    Generate Ephemeral Key Pair
            │
            ▼
Exchange Public Keys
            │
            ▼
ECDH Shared Secret
            │
            ▼
HKDF (handled in hybrid_crypto.py)

Official cryptography APIs:
    ec.generate_private_key()
    private_key.exchange(ec.ECDH(), peer_public_key)
"""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


class ECDH:

    """
    Wrapper around the cryptography library's ECDH implementation.

    Uses:
        Curve : SECP256R1 (NIST P-256)

    Each instance owns one ephemeral EC keypair.
    """

    CURVE = ec.SECP256R1()

    def __init__(self) -> None:

        self._private_key = ec.generate_private_key(self.CURVE)

        self._public_key = self._private_key.public_key()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def private_key(self) -> ec.EllipticCurvePrivateKey:
        return self._private_key

    @property
    def public_key(self) -> ec.EllipticCurvePublicKey:
        return self._public_key

    # ------------------------------------------------------------------
    # Public Key Serialization
    # ------------------------------------------------------------------

    def public_key_bytes(self) -> bytes:
        """
        Return PEM encoded public key.
        """

        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @staticmethod
    def load_public_key(
        data: bytes,
    ) -> ec.EllipticCurvePublicKey:
        """
        Load a PEM encoded public key.
        """

        key = serialization.load_pem_public_key(data)

        if not isinstance(key, ec.EllipticCurvePublicKey):
            raise TypeError("Invalid EC public key.")

        return key

    # ------------------------------------------------------------------
    # Shared Secret
    # ------------------------------------------------------------------

    def derive_shared_secret(
        self,
        peer_public_key: ec.EllipticCurvePublicKey,
    ) -> bytes:
        """
        Compute the raw ECDH shared secret.

        Parameters
        ----------
        peer_public_key
            Receiver's public key.

        Returns
        -------
        bytes
            Raw shared secret.
        """

        return self._private_key.exchange(
            ec.ECDH(),
            peer_public_key,
        )

    def derive_shared_secret_from_bytes(
        self,
        peer_public_key_bytes: bytes,
    ) -> bytes:
        """
        Convenience helper that accepts PEM bytes.
        """

        peer_key = self.load_public_key(
            peer_public_key_bytes
        )

        return self.derive_shared_secret(peer_key)
