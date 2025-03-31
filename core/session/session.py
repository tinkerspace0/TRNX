from abc import ABC
from enum import Enum
from threading import Thread
from uuid import uuid4
from typing import TYPE_CHECKING

from core.trnx import TRNX
from core.trnx import TRNXEditor

if TYPE_CHECKING:
    from .session_manager import SessionManager

class Session(ABC):
    class SessionID:
        """
        Generates and manages unique session IDs.
        """
        _ids = {}  # Use a set to store used session IDs

        @classmethod
        def generate(cls, sess) -> str:
            sess_id = uuid4()
            while sess_id in cls._ids:
                sess_id = uuid4()
            cls._ids[sess_id] = sess
            return sess_id

    class SessionStatus(Enum):
        INITIALIZED = 0
        STARTING = 1
        RUNNING = 2
        PAUSED = 3
        STOPPING = 4
        TERMINATED = 5
        ERROR = 6

    def __init__(self, name: str, sess_type: "SessionManager.SessionType" = None):
        self.id = Session.SessionID.generate(self)
        self.name = name
        self.type = sess_type  # This will store the enum value.
        self._thread = None
        self.status = self.SessionStatus.TERMINATED
        self._shutdown = False

class TRNXSession(Session):
    """
    Manages a TRNX runtime session.
    """
    def __init__(self, name: str):
        # Import locally to avoid circular dependencies.
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.TRNX)
        self.trnx = None  # This can be set later as needed.

class FactorySession(Session):
    """
    Manages a TRNX factory (configuration) session.
    """
    def __init__(self, name: str):
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.FACTORY)
        self.trnx_editor = None  # This can be set later as needed.
