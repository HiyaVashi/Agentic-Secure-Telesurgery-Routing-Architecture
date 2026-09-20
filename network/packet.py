"""
network/packet.py
-----------------

Encrypted Packet used throughout the Garlic Routing network.

An EncryptedPacket represents the encrypted payload generated
by HybridCrypto before being encapsulated inside a Clove.

Workflow
--------

Doctor Agent
      │
      ▼
Hybrid Encryption
      │
      ▼
EncryptedPacket
      │
      ▼
Clove
"""

from __future__ import annotations

import base64
import time
import uuid

from dataclasses import dataclass, field


def _encode(data: bytes) -> str:
    """Base64 encode bytes."""
    return base64.b64encode(data).decode("utf-8")


def _decode(data: str) -> bytes:
    """Base64 decode string."""
    return base64.b64decode(data.encode("utf-8"))


@dataclass(slots=True)
class EncryptedPacket:
    """
    Encrypted network packet.

    Parameters
    ----------
    workflow_id
        Workflow identifier.

    sender
        Sending agent.

    receiver
        Destination agent.

    sender_public_key
        Sender's ephemeral ECDH public key.

    nonce
        AES-GCM nonce.

    ciphertext
        AES-GCM encrypted payload.
    """

    workflow_id: str

    sender: str

    receiver: str

    sender_public_key: bytes

    nonce: bytes

    ciphertext: bytes

    packet_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: float = field(
        default_factory=time.time
    )

    # ----------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Convert packet into JSON-safe dictionary.
        """

        return {

            "workflow_id": self.workflow_id,

            "packet_id": self.packet_id,

            "sender": self.sender,

            "receiver": self.receiver,

            "sender_public_key":
                _encode(self.sender_public_key),

            "nonce":
                _encode(self.nonce),

            "ciphertext":
                _encode(self.ciphertext),

            "timestamp":
                self.timestamp,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "EncryptedPacket":
        """
        Restore packet from JSON.
        """

        return cls(

            workflow_id=data["workflow_id"],

            packet_id=data["packet_id"],

            sender=data["sender"],

            receiver=data["receiver"],

            sender_public_key=_decode(
                data["sender_public_key"]
            ),

            nonce=_decode(
                data["nonce"]
            ),

            ciphertext=_decode(
                data["ciphertext"]
            ),

            timestamp=float(
                data["timestamp"]
            ),
        )

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------

    @property
    def payload_size(self) -> int:
        """
        Size of encrypted payload.
        """

        return len(self.ciphertext)

    @property
    def total_size(self) -> int:
        """
        Approximate packet size.
        """

        return (

            len(self.sender_public_key)

            + len(self.nonce)

            + len(self.ciphertext)

        )

    # ----------------------------------------------------------
    # Pretty Printing
    # ----------------------------------------------------------

    def __repr__(self) -> str:

        return (

            "EncryptedPacket("

            f"workflow_id='{self.workflow_id}', "

            f"packet_id='{self.packet_id}', "

            f"sender='{self.sender}', "

            f"receiver='{self.receiver}', "

            f"timestamp='{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}'"

            ")"

        )
        