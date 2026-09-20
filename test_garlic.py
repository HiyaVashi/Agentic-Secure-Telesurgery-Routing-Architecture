<<<<<<< HEAD
from network.hybrid_crypto import HybridCrypto
from network.garlic_router import GarlicRouter

# Initialize
hybrid = HybridCrypto()
router = GarlicRouter()

# Original message
message = """
{
    "diagnosis":"Acute Appendicitis",
    "urgency":"High"
}
"""

print("=" * 60)
print("ORIGINAL MESSAGE")
print("=" * 60)
print(message)

# Encrypt
packet = hybrid.encrypt(
    sender="Doctor",
    receiver="Security",
    message=message,
    workflow_id="WF001"
)

print("\nEncrypted Packet Created")
print(packet)

# Create Clove
clove = router.create_clove(packet)

print("\nClove Created")
print(clove)

# Create Garlic Message
garlic = router.create_garlic_message([clove])

print("\nGarlic Message Created")
print(garlic)

# Send through relay network
garlic, relay_logs = router.send(
    garlic,
    hops=3
)

print("\nRelay Logs")
for log in relay_logs:
    print(log)

# Extract packets
packets = router.extract_packets(garlic)

print("\nPackets Extracted")
print(packets)

# Decrypt
plaintext = hybrid.decrypt(packets[0])

print("\nRecovered Message")
=======
from network.hybrid_crypto import HybridCrypto
from network.garlic_router import GarlicRouter

# Initialize
hybrid = HybridCrypto()
router = GarlicRouter()

# Original message
message = """
{
    "diagnosis":"Acute Appendicitis",
    "urgency":"High"
}
"""

print("=" * 60)
print("ORIGINAL MESSAGE")
print("=" * 60)
print(message)

# Encrypt
packet = hybrid.encrypt(
    sender="Doctor",
    receiver="Security",
    message=message,
    workflow_id="WF001"
)

print("\nEncrypted Packet Created")
print(packet)

# Create Clove
clove = router.create_clove(packet)

print("\nClove Created")
print(clove)

# Create Garlic Message
garlic = router.create_garlic_message([clove])

print("\nGarlic Message Created")
print(garlic)

# Send through relay network
garlic, relay_logs = router.send(
    garlic,
    hops=3
)

print("\nRelay Logs")
for log in relay_logs:
    print(log)

# Extract packets
packets = router.extract_packets(garlic)

print("\nPackets Extracted")
print(packets)

# Decrypt
plaintext = hybrid.decrypt(packets[0])

print("\nRecovered Message")
>>>>>>> a622173226c4d140cf54d90651d3ec0bdfa4d2dc
print(plaintext)