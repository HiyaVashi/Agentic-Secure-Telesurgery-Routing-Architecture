import random
import time

from network.garlic_message import GarlicMessage


class Relay:
    """
    Simulates a Garlic Routing relay node.
    """

    def __init__(self, relay_id: str):
        self.relay_id = relay_id

    def forward(self, garlic_message: GarlicMessage):

        start = time.perf_counter()

        # Simulate relay processing delay
        delay = random.uniform(0.05, 0.20)
        time.sleep(delay)

        processing_time = round(
            time.perf_counter() - start,
            4
        )

        print(f"\n[{self.relay_id}]")
        print(f"Forwarding Garlic Message : {garlic_message.garlic_id}")
        print(f"Number of Cloves          : {garlic_message.total_cloves()}")
        print(f"Processing Time           : {processing_time} sec")

        log = {
            "relay": self.relay_id,
            "processing_time": processing_time
        }

        return garlic_message, log