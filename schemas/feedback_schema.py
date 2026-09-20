from pydantic import BaseModel
class FeedbackDecision(BaseModel):
    proceed: bool
    action: str
    reason: str
    confidence: str