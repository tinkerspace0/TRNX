# api/shared/schemas.py
from pydantic import BaseModel

class CreateProjectRequest(BaseModel):
    name: str