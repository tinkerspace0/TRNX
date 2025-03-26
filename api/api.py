# api/api.py

from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel

from trenex import TrenexServer

app = FastAPI()

# Pydantic model for session creation
class CreateSessionRequest(BaseModel):
    name: str
    session_type: str  # "TRNX" or "FACTORY"


@app.on_event("startup")
async def startup_event():
    server = TrenexServer()
    app.state.server = server
    server.mark_running()
    print("TrenexServer initialized and attached to app.state")

@app.on_event("shutdown")
async def shutdown_event():
    server = getattr(app.state, "server", None)
    if server:
       server.shutdown()

def get_trenex_server(request: Request):
    server = getattr(request.app.state, "server", None)
    if not server:
        raise HTTPException(status_code=500, detail="TrenexServer not initialized")
    return server


# API Endpoints

@app.get("/sessions/")
def list_sessions(server: TrenexServer = Depends(get_trenex_server)):
    sessions = server.session_manager.all_sessions
    return {"sessions": sessions}

@app.post("/sessions/")
def create_session(payload: CreateSessionRequest, server: TrenexServer = Depends(get_trenex_server)):
    try:
        session_type_enum = server.session_manager.SessionType[payload.session_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid session type: {payload.session_type}")
    
    try:
        session_id, session = server.session_manager.start_new_session(payload.name, session_type_enum)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
    return {
        "id": str(session_id),
        "name": session.name,
        "type": payload.session_type.lower()
    }