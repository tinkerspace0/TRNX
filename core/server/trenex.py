# core/server/trenex.py

from enum import Enum
from core.debug.logger import gl_logger
from core.session import SessionManager

class TrenexServer:
    """
    TrenexServer is the central backend application.
    It holds the session manager and other core systems.
    """
    class TrenexStatus(Enum):
        INITIALIZED = 0
        RUNNING = 1
        PAUSED = 2
        TERMINATED = 3
        STOPPED = 4
        ERROR = 5

    def __init__(self):
        self.name = "Trenex Backend"
        self._ssm = SessionManager()
        self.status = self.TrenexStatus.INITIALIZED

    def mark_running(self):
        self.state = self.TrenexStatus.RUNNING
        gl_logger.info(f"{self.name} started. State: {self.state.name}")

    def new_proj(self, proj_name:str):
        self._ssm.start_new_session(name=proj_name, session_type=SessionManager.SessionType.FACTORY)

    def shutdown(self):
        for session in self.session_manager._sessions.values():
            session.shutdown()
        self.state = self.TrenexState.STOPPED
        gl_logger.info("Trenex server shutting down.")
