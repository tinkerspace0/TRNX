# api/fastapi/dependencies.py
from fastapi import Request, HTTPException

def get_trenex_server(request: Request):
    server = getattr(request.app.state, "trenex_server", None)
    if not server:
        raise HTTPException(status_code=500, detail="TrenexServer not initialized")
    return server