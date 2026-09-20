from network.clove import Clove
from network.garlic_message import GarlicMessage
from network.relay_manager import RelayManager


class GarlicRouter:
    """
    Handles Garlic Routing.

    Responsibilities:
    - Wrap packets into Cloves
    - Bundle Cloves into Garlic Messages
    - Forward through RelayManager
    - Extract packets at destination
    """

    def __init__(self):

        self.relay_manager = RelayManager()

    def create_clove(
        self,
        packet,
        priority: int = 1
    ):

        return Clove(

            destination=packet.receiver,

            priority=priority,

            packet=packet
        )

    def create_garlic_message(
        self,
        cloves
    ):

        garlic = GarlicMessage()

        for clove in cloves:
            garlic.add_clove(clove)

        return garlic

    def send(
        self,
        garlic_message,
        hops=3
    ):

        garlic_message, relay_logs = self.relay_manager.forward(
            garlic_message,
            hops
        )

        return garlic_message, relay_logs

    def extract_packets(
        self,
        garlic_message
    ):

        packets = []

        for clove in garlic_message.cloves:
            packets.append(clove.packet)

        return packets