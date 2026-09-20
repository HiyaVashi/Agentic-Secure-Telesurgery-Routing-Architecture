from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from network.key_manager import KeyManager
from network.ecdh import ECDHManager

keys = KeyManager()
ecdh = ECDHManager()

doctor_key = ecdh.derive_shared_key(
    keys.get_private_key("doctor"),
    keys.get_public_key("security"),
)

security_key = ecdh.derive_shared_key(
    keys.get_private_key("security"),
    keys.get_public_key("doctor"),
)

print(doctor_key == security_key)
print(len(doctor_key))