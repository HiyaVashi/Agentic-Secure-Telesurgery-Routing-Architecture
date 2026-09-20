from pydantic import BaseModel
from typing import List


class DoctorDiagnosis(BaseModel):
    patient_id: str
    diagnosis: str
    recommended_surgery: str
    urgency: str
    estimated_duration: str
    required_tools: List[str]
    risk_level: str
    confidence: str