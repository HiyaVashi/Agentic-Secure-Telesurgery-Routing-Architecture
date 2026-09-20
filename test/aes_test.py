from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT))

from network.aes import AES256GCM

key = AES256GCM.generate_key()

cipher = AES256GCM(key)

message = b"Remote surgery packet"

nonce, ciphertext = cipher.encrypt(message)

plaintext = cipher.decrypt(
    nonce,
    ciphertext,
)

print(plaintext)
