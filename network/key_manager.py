"""
network/key_manager.py
----------------------

Central key manager for the telesurgery network.

Maintains long-term ECDH key pairs for every participant.

Architecture
------------

Doctor Agent
Feedback Agent
Security Agent
Protocol Agent
Robotic Agent
Relay Nodes
Backup Surgeon

Each participant owns a persistent ECDH keypair.

HybridCrypto creates ephemeral sender keys while these
long-term keys represent the receiver identities.
"""

from __future__ import annotations

from .ecdh import ECDH


class KeyManager:
    """
    Stores ECDH identities for every participant.
    """

    def __init__(self) -> None:

        self._participants: dict[str, ECDH] = {}

    # ----------------------------------------------------------
    # Registration
    # ----------------------------------------------------------

    def register(self, participant: str) -> None:
        """
        Register a participant.

        Does nothing if already registered.
        """

        if participant not in self._participants:
            self._participants[participant] = ECDH()

    # ----------------------------------------------------------
    # Lookup
    # ----------------------------------------------------------

    def exists(self, participant: str) -> bool:
        return participant in self._participants

    def get_ecdh(self, participant: str) -> ECDH:

        if participant not in self._participants:
            raise KeyError(
                f"Participant '{participant}' not registered."
            )

        return self._participants[participant]

    def get_public_key(self, participant: str) -> bytes:

        return self.get_ecdh(
            participant
        ).public_key_bytes()

    def get_private_key(self, participant: str):

        return self.get_ecdh(
            participant
        ).private_key

    # ----------------------------------------------------------
    # Utilities
    # ----------------------------------------------------------

    def remove(self, participant: str) -> None:

        self._participants.pop(
            participant,
            None,
        )

    def clear(self) -> None:

        self._participants.clear()

    def participants(self) -> list[str]:

        return sorted(
            self._participants.keys()
        )
    