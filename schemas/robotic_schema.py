from pydantic import BaseModel


class RoboticResponse(BaseModel):
    status: str
    action: str
    message: str