# api/fastapi/endpoints/trenex.py
from fastapi import APIRouter, Depends, HTTPException
from api.shared.schemas import CreateProjectRequest
from api.fastapi.dependencies import get_trenex_server
from trenex import TrenexServer  # for type hints

router = APIRouter()

@router.get("/projects/")
def list_projects(server: TrenexServer = Depends(get_trenex_server)):
    sessions = server._ssm.all_sessions
    # Filter for projects (factory sessions)
    projects = [s for s in sessions if s.get("type", "").lower() == "factory"]
    return {"projects": projects}

@router.post("/projects/")
def create_project(payload: CreateProjectRequest, server: TrenexServer = Depends(get_trenex_server)):
    try:
        session_type_enum = server.session_manager.SessionType.FACTORY
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project type")
    try:
        session_id, session = server.session_manager.start_new_session(payload.name, session_type_enum)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    return {
        "id": str(session_id),
        "name": session.name,
        "type": "trenex"
    }
