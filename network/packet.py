from pydantic import BaseModel


class EncryptedPacket(BaseModel):
    workflow_id: str

    packet_id: str

    sender: str

    receiver: str

    ciphertext: str

    nonce: str

    timestamp: str