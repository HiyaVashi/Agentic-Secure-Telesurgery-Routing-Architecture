from pydantic import BaseModel


class SecurityAssessment(BaseModel):

    attack_detected: bool

    attack_type: str

    severity: str

    confidence: str

    recommended_action: str