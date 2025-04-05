# core/server/trenex.py

from enum import Enum
from typing import Tuple
from uuid import UUID

from core.debug.logger import gl_logger
from core.session import SessionManager
from core.node.manager import NodeManager
class TrenexServer:
    """
    TrenexServer is the central backend application.
    It holds the session manager and other core systems.
    """
    class TrenexStatus(Enum):
        INITIALIZED = 0
        STARTING = 1
        RUNNING = 2
        PAUSED = 3
        STOPPING = 4
        TERMINATED = 5
        ERROR = 6

    def __init__(self):
        self.name = "Trenex Backend"
        self._ssm: SessionManager = None
        self._nm = NodeManager()
        self.status = self.TrenexStatus.INITIALIZED

    def start(self):
        self.status = self.TrenexStatus.STARTING
        
        self._ssm = SessionManager()
        
        self.status = self.TrenexStatus.RUNNING
        gl_logger.info(f"TrenexServer started. State: {self.status}")

    def shutdown(self):
        self.status = self.TrenexStatus.STOPPING
        proj = self._ssm._proj_sess
        if proj:
            proj.shutdown()
        for sess in self._ssm._trnx_sess:
            sess.shutdonw()
        del self._ssm
        self.status = self.TrenexStatus.TERMINATED
        gl_logger.info("Trenex server shutting down.")
