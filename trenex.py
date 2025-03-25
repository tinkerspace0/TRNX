import uvicorn
from enum import Enum

from core.debug.logger import gl_logger
from api.api import app  # This is your FastAPI app instance
from core.session import SessionManager

class TrenexServer:
    """
    TrenexApplication is the main backend application.
    It holds the session manager (and eventually other subsystems like TRNX objects)
    and exposes a unified interface for controlling sessions and other core features.
    """
    class TrenexState(Enum):
        """
        Enum-like class to represent the state of the Trenex application.
        """
        INITIALIZED, RUNNING, PAUSED, TERMINATED, STOPPED, ERROR = range(6)
        
    def __init__(self):
        self.name = "Trenex Backend"
        self.session_manager = SessionManager()  # Your session manager instance
        self.state = self.TrenexState.INITIALIZED

    def start(self):
        """Start the Trenex application (initialize subsystems, etc.)."""
        
        gl_logger.info("Starting uvicorn server on http://0.0.0.0:8000 ...")
        # Start the FastAPI server
        # Note: You can also use `uvicorn.run(app, ...)` directly in the main block.
        # Here, we are using the `app` instance from api/api.py.
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
        self.status = self.TrenexState.RUNNING
        app.state.trenex_server = self  # Attach the Trenex server instance to FastAPI's state.
        gl_logger.info("Trenex server started.")
        
        # TODO: Add any additional initialization logic here.

    def shutdown(self):
        """Shut down the Trenex application gracefully."""
        # Iterate over sessions and perform any required cleanup.
        for session in self.session_manager._sessions.values():
            session.shutdown()  # Ensure each session is properly stopped.
        self.status = self.TrenexState.STOPPED
        gl_logger.info("Trenex server shutting down...")
        # Optionally, you can also stop the FastAPI server here.
    
if __name__ == "__main__":
    server = TrenexServer()
    server.start()