"""
network/garlic_router.py
------------------------

Garlic Routing Engine.

Responsible for selecting a relay path for Garlic Messages.

The router does NOT forward messages.

It only constructs a secure multi-hop path which is then
executed by RelayManager.
"""

from __future__ import annotations

import random

from .relay import Relay
from .relay_manager import RelayManager
from .garlic_message import GarlicMessage


class GarlicRouter:
    """
    Garlic Routing Engine.
    """

    def __init__(
        self,
        relay_manager: RelayManager,
    ) -> None:

        self.relay_manager = relay_manager

    # ----------------------------------------------------------
    # Route Selection
    # ----------------------------------------------------------

    def build_route(
        self,
        hops: int = 3,
    ) -> list[Relay]:
        """
        Construct a relay path.

        Strategy
        --------
        1. Ignore offline relays
        2. Sort by trust score
        3. Randomly choose from the highest trusted relays
        """

        available = [

            relay

            for relay in self.relay_manager.relays

            if relay.online

        ]

        if len(available) < hops:

            raise RuntimeError(
                "Not enough online relays."
            )

        # Highest trust first

        available.sort(

            key=lambda relay: relay.trust_score,

            reverse=True,

        )

        # Keep only the best relays

        top_relays = available[: max(hops * 2, hops)]

        # Randomize among trusted relays

        route = random.sample(
            top_relays,
            hops,
        )

        return route

    # ----------------------------------------------------------
    # Route Message
    # ----------------------------------------------------------

    def route(
        self,
        garlic: GarlicMessage,
        hops: int = 3,
    ) -> GarlicMessage:
        """
        Build a route and execute it.
        """

        route = self.build_route(hops)

        return self.relay_manager.execute_route(
            garlic,
            route,
        )

    # ----------------------------------------------------------
    # Display
    # ----------------------------------------------------------

    @staticmethod
    def print_route(
        route: list[Relay],
    ) -> None:

        print()

        print("=" * 60)

        print("Selected Relay Path")

        print("=" * 60)

        for relay in route:

            print(relay.relay_id)

        print("=" * 60)
        