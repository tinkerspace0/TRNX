# api/fastapi/app.py
from fastapi import FastAPI
from api.events import lifespan
from api.fastapi.endpoints import trenex, trnx

app = FastAPI(title="Trenex API", lifespan=lifespan)

app.include_router(trenex.router, prefix="/trenex")
app.include_router(trnx.router, prefix="/trnx")
