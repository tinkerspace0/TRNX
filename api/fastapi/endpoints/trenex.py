# api/fastapi/endpoints/trenex.py

from fastapi import APIRouter, Depends, HTTPException

from api.shared.schemas import CreateProjectRequest
from api.shared.schemas import NodeRequest, ConnectNodeIORequest
from api.fastapi.dependencies import get_trenex_server

from core.server.trenex import TrenexServer  # for type hints
from core.node.utils import get_available_nodes

router = APIRouter()

# General project endpoints
@router.get("/project/")
def project(server: TrenexServer = Depends(get_trenex_server)):
    # Get all sessions from the session manager and filter only factory sessions (projects)
    proj = server._ssm.project
    result = {}
    if proj:
        result = {
            "id": str(proj.id),
            "name": proj.name,
            "status": proj.status.name.lower(),
            "type": proj.type.name.lower() if proj.type is not None else "unknown"
            }
    return result

# project/info

@router.post("/project/")
def create_project(
    payload: CreateProjectRequest,
    server: TrenexServer = Depends(get_trenex_server)
):
    try:
        proj = server._ssm.start_new_project(payload.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    return {
        "id": str(proj.id),
        "name": proj.name,
        "status": proj.status.name.lower(),
        "type": proj.type.name.lower() if proj.type is not None else "unknown"
        }

@router.get("/nodes/")
def available_nodes():    
    try:
        nodes = get_available_nodes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return nodes


# Node operation Endpoints
@router.post("/node/attach")
def attach_node(payload: NodeRequest, server: TrenexServer = Depends(get_trenex_server)):
    try:
        server._ssm.project._exec.attach_node(payload.type, payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"remark": f"Node '{payload.name}' attached successfully."}

@router.post("/node/detach")
def detach_node(payload: NodeRequest, server: TrenexServer = Depends(get_trenex_server)):
    try:
        server._ssm.project._exec.detach_node(payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"remark": f"Node '{payload.name}' detached successfully."}

@router.post("/node/connect")
def connect_node_io(payload: ConnectNodeIORequest, server: TrenexServer = Depends(get_trenex_server)):
    try:
        server._ssm.project._exec.connect_node_io(
            payload.output_node_name, payload.output_port,
            payload.input_node_name, payload.input_port
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"remark": "Nodes connected successfully."}

@router.post("/project/build")
def build_project(server: TrenexServer = Depends(get_trenex_server)):
    try:
        server._ssm.project._exec.build_trnx()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"remark": "TRNX project built successfully."}
