from pydantic import BaseModel


class DiagnosisEvaluation(BaseModel):
    predicted: str
    expected: str
    correct: bool
    score: float


class SecurityEvaluation(BaseModel):
    predicted_attack_detected: bool
    expected_attack_detected: bool

    predicted_attack: str
    expected_attack: str

    predicted_action: str
    expected_action: str

    attack_detection_correct: bool
    attack_type_correct: bool
    action_correct: bool

    score: float


class ProtocolEvaluation(BaseModel):
    predicted: str
    expected: str
    correct: bool
    score: float


class FeedbackEvaluation(BaseModel):
    predicted_action: str
    expected_action: str
    correct: bool
    score: float


class RobotEvaluation(BaseModel):

    predicted_status: str
    expected_status: str

    predicted_action: str
    expected_action: str

    status_correct: bool
    action_correct: bool

    score: float