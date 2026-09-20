import json

from agents.protocol import ProtocolSwitcherAgent
from models.llm import get_llm


llm = get_llm()

agent = ProtocolSwitcherAgent(llm)


security_report = {
    "attack_detected": True,
    "attack_type": "ddos",
    "confidence": 0.98,
    "severity": "high"
}


network_metrics = {
    "latency_ms": 90,
    "jitter_ms": 130,
    "packet_loss_pct": 8,
    "bandwidth_mbps": 20,
    "link_quality": "poor"
}


result = agent.run(
    security_report,
    network_metrics
)

print(json.dumps(result, indent=4))