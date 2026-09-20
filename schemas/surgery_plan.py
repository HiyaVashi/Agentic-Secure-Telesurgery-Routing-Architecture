from pydantic import BaseModel

class SurgeryPlan(BaseModel):

    patient_id: str

    surgery_type: str

    risk_level: str

    estimated_duration_minutes: int

    required_tools: list[str]

    protocol_preference: str

    pre_op_checklist: list[str]

    surgical_steps: list[str]

    status: str