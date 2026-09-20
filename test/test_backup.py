import json

from agents.backup import BackupSurgeonAgent
from models.llm import get_llm

llm = get_llm()

backup = BackupSurgeonAgent(llm)

arm_result = {
    "status": "failed",
    "step_number": 4,
    "remarks": "Loss of robotic arm communication"
}

surgery_plan = {
    "patient_id": "PT001",
    "surgery_type": "heart_bypass",
    "surgical_steps": [
        "Incision",
        "Expose artery",
        "Bypass",
        "Closure"
    ]
}

result = backup.run(
    arm_result,
    surgery_plan
)

print(json.dumps(result, indent=4))