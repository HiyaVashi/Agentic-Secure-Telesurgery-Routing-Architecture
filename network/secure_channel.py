"""
network/secure_channel.py
-------------------------

High-level secure communication layer.

Agents only interact with:

    send()
    receive()

The secure channel internally performs:

    Hybrid Encryption
            │
            ▼
      EncryptedPacket
            │
            ▼
          Clove
            │
            ▼
      Garlic Message
            │
            ▼
      Garlic Routing
            │
            ▼
      Relay Network
"""

from __future__ import annotations

import json

from .clove import Clove
from .garlic_message import GarlicMessage
from .garlic_router import GarlicRouter
from .hybrid_crypto import HybridCrypto
from .key_manager import KeyManager
from .relay_manager import RelayManager


class SecureChannel:

    def __init__(
        self,
        key_manager: KeyManager,
        relay_manager: RelayManager,
    ) -> None:

        self.key_manager = key_manager
        self.relay_manager = relay_manager

        self.router = GarlicRouter(
            relay_manager
        )

        self.crypto = HybridCrypto()

    # ----------------------------------------------------------
    # SEND
    # ----------------------------------------------------------

    def send(
        self,
        sender: str,
        receiver: str,
        workflow_id: str,
        message: dict | str,
        hops: int = 3,
    ) -> GarlicMessage:

        if isinstance(message, dict):

            plaintext = json.dumps(
                message
            ).encode("utf-8")

        else:

            plaintext = str(
                message
            ).encode("utf-8")

        packet = self.crypto.encrypt(

            plaintext=plaintext,

            receiver_public_key=
            self.key_manager.get_public_key(
                receiver
            ),

            workflow_id=workflow_id,

            sender=sender,

            receiver=receiver,
        )

        clove = Clove(

            packet=packet,

            destination=receiver,
        )

        garlic = GarlicMessage()

        garlic.add_clove(
            clove
        )

        garlic = self.router.route(

            garlic,

            hops=hops,
        )

        return garlic

    # ----------------------------------------------------------
    # RECEIVE
    # ----------------------------------------------------------

    def receive(
        self,
        garlic: GarlicMessage,
        receiver: str,
    ) -> dict | str:

        if garlic.clove_count == 0:

            raise ValueError(
                "Garlic Message contains no cloves."
            )

        packet = garlic.cloves[0].packet

        plaintext = self.crypto.decrypt(

            packet,

            self.key_manager.get_ecdh(
                receiver
            ),
        )

        try:

            return json.loads(
                plaintext.decode(
                    "utf-8"
                )
            )

        except json.JSONDecodeError:

            return plaintext.decode(
                "utf-8"
            )
    