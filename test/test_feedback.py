import json

from agents.feedback import FeedbackAgent
from models.llm import get_llm


llm = get_llm()

feedback = FeedbackAgent(llm)


with open("diagnosis.json") as f:
    diagnosis = json.load(f)[0]

with open("traffic.json") as f:
    traffic = json.load(f)

doctor_output = {
    "patient_id": diagnosis["patient_id"],
    "surgery_type": "heart_bypass",
    "patient_status": "stable",
    "risk_level": "medium",
    "priority": "urgent",
    "surgical_steps": [
        "Incision",
        "Bypass",
        "Closure"
    ]
}

security_output = {
    "attack_detected": False,
    "severity": "low",
    "recommended_action": "continue",
}

protocol_output = {
    "recommended_protocol": "TCP",
    "status": "stable",
}

result = feedback.run(
    doctor_output,
    security_output,
    protocol_output,
)

print(json.dumps(result, indent=4))