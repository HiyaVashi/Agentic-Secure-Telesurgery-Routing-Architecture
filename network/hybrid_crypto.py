import uuid
from datetime import datetime

from network.aes import AESHandler
from network.ecc import ECCHandler
from network.key_manager import KeyManager
from network.packet import EncryptedPacket


class HybridCrypto:

    def __init__(self):

        self.key_manager = KeyManager()

        self.key_manager.register_agent("Doctor")
        self.key_manager.register_agent("Security")
        self.key_manager.register_agent("Protocol")
        self.key_manager.register_agent("Feedback")
        self.key_manager.register_agent("Robot")

    def encrypt(
        self,
        sender: str,
        receiver: str,
        message: str,
        workflow_id: str
    ) -> EncryptedPacket:

        # Get ECC keys
        sender_private = self.key_manager.get_private_key(sender)
        receiver_public = self.key_manager.get_public_key(receiver)

        # Derive AES key using ECDH
        aes_key = ECCHandler.derive_shared_key(
            sender_private,
            receiver_public
        )

        # Encrypt message
        encrypted = AESHandler.encrypt(
            plaintext=message,
            key=aes_key
        )

        # Create packet
        packet = EncryptedPacket(

            workflow_id=workflow_id,

            packet_id=str(uuid.uuid4()),

            sender=sender,

            receiver=receiver,

            ciphertext=encrypted["ciphertext"],

            nonce=encrypted["nonce"],

            timestamp=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        return packet

    def decrypt(
        self,
        packet: EncryptedPacket
    ) -> str:

        # Get ECC keys
        receiver_private = self.key_manager.get_private_key(
            packet.receiver
        )

        sender_public = self.key_manager.get_public_key(
            packet.sender
        )

        # Derive same AES key
        aes_key = ECCHandler.derive_shared_key(
            receiver_private,
            sender_public
        )

        # Decrypt
        plaintext = AESHandler.decrypt(
            ciphertext=packet.ciphertext,
            nonce=packet.nonce,
            key=aes_key
        )

        return plaintext