# api/events.py
from contextlib import asynccontextmanager
from core.controller import TrenexController

@asynccontextmanager
async def lifespan(app):
    server = TrenexController()
    app.state._server = server
    print("TrenexServer initialized and attached to app.state")
    server.start()
    print("TrenexServer started")
    yield
    server.shutdown()
    print("TrenexServer shut down")
