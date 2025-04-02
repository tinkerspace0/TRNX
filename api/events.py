# api/events.py
from contextlib import asynccontextmanager
from core.server.trenex import TrenexServer

@asynccontextmanager
async def lifespan(app):
    server = TrenexServer()
    app.state._server = server
    print("TrenexServer initialized and attached to app.state")
    server.start()
    print("TrenexServer started")
    yield
    server.shutdown()
    print("TrenexServer shut down")
