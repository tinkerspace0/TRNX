# api/events.py
from contextlib import asynccontextmanager
from core.server.trenex import TrenexServer

@asynccontextmanager
async def lifespan(app):
    server = TrenexServer()
    app.state._server = server
    server.mark_running()
    print("TrenexServer initialized and attached to app.state")
    yield
    server.shutdown()
    print("TrenexServer shut down")
