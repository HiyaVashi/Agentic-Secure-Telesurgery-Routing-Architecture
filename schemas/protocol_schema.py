from pydantic import BaseModel


class ProtocolDecision(BaseModel):
    protocol: str
    reason: str
    expected_latency: str
    security_level: str