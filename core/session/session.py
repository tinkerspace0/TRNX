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
        _ids = set()  # Use a set to store used session IDs

        @classmethod
        def generate(cls, session) -> str:
            session_id = uuid4()
            while session_id in cls._ids:
                session_id = uuid4()
            cls._ids.add(session_id)
            return session_id

    class SessionStatus(Enum):
        INITIALIZED = 0
        RUNNING = 1
        PAUSED = 2
        TERMINATED = 3
        STOPPED = 4
        ERROR = 5

    def __init__(self, name: str, session_type: "SessionManager.SessionType" = None):
        self.id = Session.SessionID.generate(self)
        self.name = name
        self.type = session_type  # This will store the enum value.
        self.thread = None
        self.status = self.SessionStatus.INITIALIZED
        self._shutdown = False

class TRNXSession(Session):
    """
    Manages a TRNX runtime session.
    """
    def __init__(self, name: str, trnx: TRNX = None):
        # Import locally to avoid circular dependencies.
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.TRNX)
        self.trnx = trnx  # This can be set later as needed.

class FactorySession(Session):
    """
    Manages a TRNX factory (configuration) session.
    """
    def __init__(self, name: str, trnx_editor: TRNXEditor = None):
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.FACTORY)
        self.trnx_editor = trnx_editor  # This can be set later as needed.
