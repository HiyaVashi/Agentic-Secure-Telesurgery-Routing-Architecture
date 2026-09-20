"""
network/clove.py
----------------

A Clove is the smallest routing unit inside a Garlic Message.

Each Clove contains exactly ONE encrypted packet together with
routing metadata required by the relay network.

Workflow
--------

EncryptedPacket
        │
        ▼
      Clove
        │
        ▼
 Garlic Message
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from .packet import EncryptedPacket


@dataclass(slots=True)
class Clove:
    """
    Garlic Routing Clove.

    One Clove transports one EncryptedPacket.

    Parameters
    ----------
    clove_id
        Unique identifier.

    packet
        Encrypted payload.

    destination
        Final recipient.

    ttl
        Remaining relay hops.

    created_at
        Unix timestamp.

    relay_history
        Relay nodes that forwarded this clove.
    """

    packet: EncryptedPacket

    destination: str

    ttl: int = 5

    clove_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: float = field(
        default_factory=time.time
    )

    relay_history: list[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------------
    # Relay Operations
    # --------------------------------------------------------------

    def visit(self, relay_name: str) -> None:
        """
        Record traversal through a relay.
        """

        self.relay_history.append(relay_name)

        if self.ttl > 0:
            self.ttl -= 1

    @property
    def expired(self) -> bool:
        """
        Has the clove exceeded its relay limit?
        """

        return self.ttl <= 0

    # --------------------------------------------------------------
    # Serialization
    # --------------------------------------------------------------

    def to_dict(self) -> dict:

        return {
            "clove_id": self.clove_id,
            "destination": self.destination,
            "ttl": self.ttl,
            "created_at": self.created_at,
            "relay_history": self.relay_history,
            "packet": self.packet.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "Clove":

        return cls(
            packet=EncryptedPacket.from_dict(
                data["packet"]
            ),
            destination=data["destination"],
            ttl=data["ttl"],
            clove_id=data["clove_id"],
            created_at=data["created_at"],
            relay_history=list(
                data.get(
                    "relay_history",
                    [],
                )
            ),
        )

    # --------------------------------------------------------------
    # Information
    # --------------------------------------------------------------

    @property
    def packet_size(self) -> int:
        """
        Size of the encrypted payload.
        """

        return self.packet.total_size

    @property
    def hop_count(self) -> int:
        """
        Number of relays visited.
        """

        return len(self.relay_history)

    @property
    def current_relay(self) -> str | None:
        """
        Most recent relay.
        """

        if not self.relay_history:
            return None

        return self.relay_history[-1]
