import random

from network.relay import Relay
from network.garlic_message import GarlicMessage


class RelayManager:
    """
    Creates relay nodes and forwards
    Garlic Messages through them.
    """

    def __init__(self, number_of_relays: int = 5):

        self.relays = [
            Relay(f"Relay-{i+1}")
            for i in range(number_of_relays)
        ]

    def generate_path(self, hops: int = 3):

        """
        Randomly select relay nodes.
        """

        return random.sample(
            self.relays,
            hops
        )

    def forward(
        self,
        garlic_message: GarlicMessage,
        hops: int = 3
    ):

        relay_path = self.generate_path(hops)

        garlic_message.relay_path = [
            relay.relay_id
            for relay in relay_path
        ]

        relay_logs = []

        print("\nSelected Relay Path")
        print("----------------------------")

        for relay in relay_path:

            print(relay.relay_id)

        print("----------------------------")

        for relay in relay_path:

            garlic_message, log = relay.forward(
                garlic_message
            )

            relay_logs.append(log)

        return garlic_message, relay_logs