from abc import ABC, abstractmethod
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

        self._exec = None

    @abstractmethod
    def initialize(self):
        """
        Session Initialization related code
        """
        raise NotImplementedError("Initialisation code has to implemented by different types of sessions based on their needs")
class TRNXSession(Session):
    """
    Manages a TRNX runtime session.
    """
    def __init__(self, name: str):
        # Import locally to avoid circular dependencies.
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.TRNX)

    def initialize(self):
        pass
        # self._exec = TRNX.load()
        # self.status = Session.SessionStatus.INITIALIZED

class FactorySession(Session):
    """
    Manages a TRNX factory (configuration) session.
    """
    def __init__(self, name: str):
        from core.session.session_manager import SessionManager
        super().__init__(name, session_type=SessionManager.SessionType.FACTORY)

    def initialize(self):
        self._exec = TRNXEditor()
        self.status = Session.SessionStatus.INITIALIZED