"""
network/relay.py
----------------

Relay Node implementation.

A Relay receives a GarlicMessage, records forwarding metadata,
updates every Clove's relay history, decrements TTL and forwards
the GarlicMessage.

A Relay NEVER decrypts payloads.

Workflow
--------

GarlicMessage
        │
        ▼
      Relay
        │
        ▼
GarlicMessage
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from tracemalloc import start

from .garlic_message import GarlicMessage


@dataclass(slots=True)
class Relay:
    """
    Garlic Routing Relay Node.

    Parameters
    ----------
    relay_id
        Unique relay identifier.

    trust_score
        Relay reliability score (0.0–1.0).

    processing_delay_ms
        Artificial forwarding delay.

    online
        Relay availability.
    """

    relay_id: str

    trust_score: float = 1.0

    processing_delay_ms: float = 2.0

    online: bool = True

    # ----------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------

    messages_forwarded: int = 0

    cloves_forwarded: int = 0

    dropped_messages: int = 0

    total_processing_time_ms: float = 0.0

    last_seen: float | None = None

    # ----------------------------------------------------------
    # Forwarding
    # ----------------------------------------------------------

    def forward(
        self,
        garlic: GarlicMessage,
    ) -> GarlicMessage:
        """
        Forward a GarlicMessage.
        """

        if not self.online:

            self.dropped_messages += 1

            raise RuntimeError(
                f"{self.relay_id} is offline."
            )

        start = time.perf_counter()

        time.sleep(
            self.processing_delay_ms / 1000
        )

        for clove in garlic:

            if clove.expired:
                continue

            clove.visit(
                self.relay_id
            )

        elapsed = (
            time.perf_counter() - start
        )

        self.messages_forwarded += 1

        self.cloves_forwarded += garlic.clove_count

        self.total_processing_time_ms += (
            elapsed * 1000
        )

        self.last_seen = time.time()

    # -------------------------------------------------
    # Demo Output
    # -------------------------------------------------

        print()

        print(f"[{self.relay_id}]")

        print(
            f"Forwarding Garlic Message : "
            f"{garlic.garlic_id}"
        )

        print(
            f"Number of Cloves          : "
            f"{garlic.clove_count}"
        )

        print(
            f"Processing Time           : "
            f"{elapsed:.4f} sec"
        )

        return garlic

    # ----------------------------------------------------------
    # Relay State
    # ----------------------------------------------------------

    def enable(self) -> None:
        """
        Bring relay online.
        """

        self.online = True

    def disable(self) -> None:
        """
        Take relay offline.
        """

        self.online = False

    # ----------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------

    @property
    def average_processing_time_ms(self) -> float:
        """
        Average forwarding latency.
        """

        if self.messages_forwarded == 0:
            return 0.0

        return (
            self.total_processing_time_ms
            / self.messages_forwarded
        )

    @property
    def uptime(self) -> str:
        """
        Relay status.
        """

        return (
            "Online"
            if self.online
            else "Offline"
        )

    def stats(self) -> dict:
        """
        Return relay statistics.
        """

        return {

            "relay_id": self.relay_id,

            "trust_score": round(
                self.trust_score,
                2,
            ),

            "status": self.uptime,

            "messages_forwarded": self.messages_forwarded,

            "cloves_forwarded": self.cloves_forwarded,

            "dropped_messages": self.dropped_messages,

            "average_processing_time_ms": round(
                self.average_processing_time_ms,
                3,
            ),

            "last_seen": self.last_seen,
        }

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"Relay("
            f"id='{self.relay_id}', "
            f"trust={self.trust_score:.2f}, "
            f"online={self.online}, "
            f"forwarded={self.messages_forwarded}"
            f")"
        )
    