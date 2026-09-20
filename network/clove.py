from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from network.packet import EncryptedPacket


class Clove(BaseModel):
    """
    Represents one encrypted message (Clove)
    inside a Garlic Message.
    """

    clove_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    destination: str

    priority: int = 1

    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    packet: EncryptedPacket