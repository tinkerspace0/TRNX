# api/fastapi/endpoints/trnx.py
from fastapi import APIRouter, Depends, HTTPException
from api.fastapi.dependencies import get_trenex_server
from core.controller import TrenexController

router = APIRouter()

@router.get("/status/")
def get_trnx_status(server: TrenexController = Depends(get_trenex_server)):
    # Placeholder for TRNX (runtime) endpoints.
    return {"status": "TRNX runtime endpoints not implemented yet."}
