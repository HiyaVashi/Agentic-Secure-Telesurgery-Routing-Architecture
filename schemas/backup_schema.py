from pydantic import BaseModel


class BackupDecision(BaseModel):
    activate_backup: bool
    recovery_plan: str
    immediate_action: str
    estimated_recovery_time: str
    confidence: str