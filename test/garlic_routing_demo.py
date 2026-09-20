"""
garlic_routing_demo.py

End-to-End Demonstration

Doctor
    │
    ▼
Hybrid Encryption
    │
    ▼
EncryptedPacket
    │
    ▼
Clove
    │
    ▼
Garlic Message
    │
    ▼
Garlic Router
    │
    ▼
Relay Manager
    │
    ▼
Hybrid Decryption
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json

from network.hybrid_crypto import HybridCrypto
from network.key_manager import KeyManager
from network.packet import EncryptedPacket
from network.clove import Clove
from network.garlic_message import GarlicMessage
from network.relay import Relay
from network.relay_manager import RelayManager
from network.garlic_router import GarlicRouter


# ============================================================
# ORIGINAL MESSAGE
# ============================================================

original_message = {

    "diagnosis": "Acute Appendicitis",

    "urgency": "High",

}

print("\n" + "=" * 60)

print("ORIGINAL MESSAGE")

print("=" * 60)

print()

print(
    json.dumps(
        original_message,
        indent=4,
    )
)


# ============================================================
# KEY MANAGER
# ============================================================

key_manager = KeyManager()

key_manager.register("Doctor")

key_manager.register("Security")


# ============================================================
# HYBRID ENCRYPTION
# ============================================================

crypto = HybridCrypto()

packet = crypto.encrypt(

    plaintext=json.dumps(
        original_message
    ).encode(),

    receiver_public_key=
        key_manager.get_public_key(
            "Security"
        ),

    workflow_id="WF001",

    sender="Doctor",

    receiver="Security",
)

print()

print("Encrypted Packet Created")

print(packet)
# ============================================================
# CREATE CLOVE
# ============================================================

clove = Clove(
    packet=packet,
    destination="Security",
)

print()

print("Clove Created")

print(clove)


# ============================================================
# CREATE GARLIC MESSAGE
# ============================================================

garlic = GarlicMessage()

garlic.add_clove(clove)

print()

print("Garlic Message Created")

print(garlic)


# ============================================================
# CREATE RELAY NETWORK
# ============================================================

relay_manager = RelayManager()

relay_manager.add_relay(
    Relay(
        "Relay-1",
        trust_score=0.91,
    )
)

relay_manager.add_relay(
    Relay(
        "Relay-2",
        trust_score=0.98,
    )
)

relay_manager.add_relay(
    Relay(
        "Relay-3",
        trust_score=0.87,
    )
)

relay_manager.add_relay(
    Relay(
        "Relay-4",
        trust_score=0.95,
    )
)

relay_manager.add_relay(
    Relay(
        "Relay-5",
        trust_score=0.93,
    )
)


# ============================================================
# GARLIC ROUTER
# ============================================================

router = GarlicRouter(
    relay_manager
)

route = router.build_route(
    hops=3,
)

print()

print("=" * 60)

print("Selected Relay Path")

print("=" * 60)

for relay in route:

    print(relay.relay_id)

print("=" * 60)


# ============================================================
# EXECUTE ROUTE
# ============================================================

garlic = relay_manager.execute_route(
    garlic,
    route,
)

print()

print("Relay Logs")

for log in relay_manager.relay_logs:

    print(log)

print()

print("Routing Complete")

print()

print(relay_manager.stats())
# ============================================================
# PACKETS EXTRACTED
# ============================================================

print()

print("=" * 60)

print("PACKETS EXTRACTED")

print("=" * 60)

packets = []

for clove in garlic:

    packets.append(clove.packet)

print(packets)


# ============================================================
# RECOVERED MESSAGE
# ============================================================

print()

print("=" * 60)

print("RECOVERED MESSAGE")

print("=" * 60)

receiver = key_manager.get_ecdh(
    "Security"
)

for packet in packets:

    plaintext = crypto.decrypt(
        packet,
        receiver,
    )

    recovered = json.loads(
        plaintext.decode()
    )

    print()

    print(
        json.dumps(
            recovered,
            indent=4,
        )
    )

# ============================================================
# INTEGRITY CHECK
# ============================================================

print()

print("=" * 60)

print("INTEGRITY CHECK")

print("=" * 60)

if recovered == original_message:

    print("SUCCESS")
    print("Recovered message matches original.")

else:

    print("FAILED")


# ============================================================
# VERIFY INTEGRITY
# ============================================================

print()

print("=" * 60)

print("INTEGRITY CHECK")

print("=" * 60)

if recovered == original_message:

    print()

    print("SUCCESS")

    print("Recovered message matches original.")

else:

    print()

    print("FAILED")

    print("Recovered message DOES NOT match.")