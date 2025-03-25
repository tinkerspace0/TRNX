# api/api.py
from fastapi import FastAPI, Request, HTTPException, Depends

app = FastAPI()

def get_trenex_server(request: Request):
    trenex_server = request.app.state.trenex_server
    if not trenex_server:
        raise HTTPException(status_code=500, detail="Application not initialized")
    return trenex_server

@app.get("/sessions/")
def list_sessions(trenex_app = Depends(get_trenex_server)):
    sessions = trenex_app.list_sessions()
    return {"sessions": sessions}
