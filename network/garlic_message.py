"""
network/garlic_message.py
-------------------------

Garlic Message implementation.

A Garlic Message is a container that bundles one or more
Cloves together before being forwarded through the relay
network.

Workflow
--------

EncryptedPacket
        │
        ▼
      Clove
        │
        ▼
 GarlicMessage
        │
        ▼
 Relay Manager
        │
        ▼
 Relay Nodes
"""

from __future__ import annotations

import time
import uuid

from dataclasses import dataclass, field

from .clove import Clove


@dataclass(slots=True)
class GarlicMessage:
    """
    Garlic Message.

    Bundles multiple Cloves into a single routing message.

    Parameters
    ----------
    garlic_id
        Unique Garlic Message identifier.

    cloves
        Collection of Cloves.

    created_at
        UNIX timestamp.
    """

    cloves: list[Clove] = field(default_factory=list)

    garlic_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: float = field(
        default_factory=time.time
    )

    # ----------------------------------------------------------
    # Clove Operations
    # ----------------------------------------------------------

    def add_clove(
        self,
        clove: Clove,
    ) -> None:
        """
        Add a Clove to the Garlic Message.

        Raises
        ------
        ValueError
            If the Clove already exists.
        """

        if clove.clove_id in self:
            raise ValueError(
                f"Clove '{clove.clove_id}' already exists."
            )

        self.cloves.append(clove)

    def remove_clove(
        self,
        clove_id: str,
    ) -> bool:
        """
        Remove a Clove by ID.

        Returns
        -------
        bool
            True if removed.
        """

        for index, clove in enumerate(self.cloves):

            if clove.clove_id == clove_id:

                self.cloves.pop(index)

                return True

        return False

    def get_clove(
        self,
        clove_id: str,
    ) -> Clove | None:
        """
        Retrieve a Clove by ID.
        """

        for clove in self.cloves:

            if clove.clove_id == clove_id:
                return clove

        return None

    # ----------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialize Garlic Message.
        """

        return {
            "garlic_id": self.garlic_id,
            "created_at": self.created_at,
            "cloves": [
                clove.to_dict()
                for clove in self.cloves
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "GarlicMessage":
        """
        Deserialize Garlic Message.
        """

        return cls(
            garlic_id=data["garlic_id"],
            created_at=data["created_at"],
            cloves=[
                Clove.from_dict(item)
                for item in data["cloves"]
            ],
        )

    # ----------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------

    @property
    def clove_count(self) -> int:
        """
        Number of Cloves.
        """

        return len(self.cloves)

    @property
    def total_payload_size(self) -> int:
        """
        Total encrypted payload size.
        """

        return sum(
            clove.packet_size
            for clove in self.cloves
        )

    @property
    def destinations(self) -> list[str]:
        """
        Unique destinations.
        """

        return sorted(
            {
                clove.destination
                for clove in self.cloves
            }
        )

    @property
    def expired(self) -> bool:
        """
        Returns True if every Clove has expired.
        """

        return all(
            clove.expired
            for clove in self.cloves
        )

    # ----------------------------------------------------------
    # Python Helpers
    # ----------------------------------------------------------

    def __len__(self) -> int:
        return len(self.cloves)

    def __iter__(self):
        return iter(self.cloves)

    def __getitem__(
        self,
        index: int,
    ) -> Clove:
        return self.cloves[index]

    def __contains__(
        self,
        clove_id: str,
    ) -> bool:
        return any(
            clove.clove_id == clove_id
            for clove in self.cloves
        )

    def __repr__(self) -> str:
        return (
            f"GarlicMessage("
            f"id={self.garlic_id}, "
            f"cloves={len(self.cloves)}, "
            f"payload={self.total_payload_size} bytes)"
        )
    