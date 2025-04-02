# api/shared/schemas.py
from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    name: str

# Pydantic models for node operations
class NodeRequest(BaseModel):
    type: str
    name: str
class ConnectNodeIORequest(BaseModel):
    on_name: str
    op_name: str
    in_name: str
    ip_name: str
