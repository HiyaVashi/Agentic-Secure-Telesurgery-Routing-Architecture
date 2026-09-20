from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from network.relay import Relay
from network.relay_manager import RelayManager

manager = RelayManager()

manager.add_relay(
    Relay(
        "Relay-1",
        trust_score=0.91,
    )
)

manager.add_relay(
    Relay(
        "Relay-2",
        trust_score=0.98,
    )
)

manager.add_relay(
    Relay(
        "Relay-3",
        trust_score=0.95,
    )
)

manager.route(garlic_message)