from datetime import datetime
from uuid import uuid4
from typing import List

from pydantic import BaseModel, Field

from network.clove import Clove


class GarlicMessage(BaseModel):
    """
    Represents one Garlic Message containing
    multiple encrypted Cloves.
    """

    garlic_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    cloves: List[Clove] = Field(default_factory=list)

    relay_path: List[str] = Field(default_factory=list)

    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    def add_clove(self, clove: Clove):
        """
        Add a clove to the garlic message.
        """
        self.cloves.append(clove)

    def remove_clove(self, clove_id: str):
        """
        Remove a clove by ID.
        """
        self.cloves = [
            c for c in self.cloves
            if c.clove_id != clove_id
        ]

    def total_cloves(self):
        """
        Return number of cloves.
        """
        return len(self.cloves)

    def get_destinations(self):
        """
        Return destinations of all cloves.
        """
        return [
            clove.destination
            for clove in self.cloves
        ]