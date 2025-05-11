from pydantic import BaseModel

class BashCommand(BaseModel):
    command: str
    description: str
    