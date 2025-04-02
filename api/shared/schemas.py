# api/shared/schemas.py
from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    name: str

# Pydantic models for node operations
class NodeRequest(BaseModel):
    type: str
    name: str
class ConnectNodeIORequest(BaseModel):
    output_node_name: str
    output_port: str
    input_node_name: str
    input_port: str
