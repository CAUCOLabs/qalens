from pydantic import BaseModel


class JiraConnectionStatus(BaseModel):
    connected: bool
    message: str
