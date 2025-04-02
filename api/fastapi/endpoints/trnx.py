# api/fastapi/endpoints/trnx.py
from fastapi import APIRouter, Depends, HTTPException
from api.fastapi.dependencies import get_trenex_server
from core.server import TrenexServer

router = APIRouter()

@router.get("/status/")
def get_trnx_status(server: TrenexServer = Depends(get_trenex_server)):
    # Placeholder for TRNX (runtime) endpoints.
    return {"status": "TRNX runtime endpoints not implemented yet."}
