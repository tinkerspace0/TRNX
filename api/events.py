# api/events.py
from contextlib import asynccontextmanager
from core.server import TrenexServer

@asynccontextmanager
async def lifespan(app):
    server = TrenexServer()
    app.state.trenex_server = server
    server.mark_running()
    print("TrenexServer initialized and attached to app.state")
    yield
    server.shutdown()
    print("TrenexServer shut down")
