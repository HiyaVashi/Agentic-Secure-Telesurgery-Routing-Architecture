from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.hybrid_crypto import HybridCrypto
from network.key_manager import KeyManager

crypto = HybridCrypto()

key_manager = KeyManager()

key_manager.register("feedback_agent")

message = b"Hello"

packet = crypto.encrypt(
    message,
    key_manager.get_public_key("feedback_agent"),
)

plaintext = crypto.decrypt(
    packet,
    key_manager.get_ecdh("feedback_agent"),
)

print(plaintext)