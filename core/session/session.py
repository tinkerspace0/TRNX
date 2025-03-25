
from abc import ABC
from enum import Enum
from threading import Thread
from typing import Dict
from uuid import uuid4


from core.trnx import TRNX
from core.trnx.factory import TRNXEditor


class Session(ABC):
    class SessionID:
        """
        Class to generate and manage session IDs.
        """
        _ids = Dict[str, None]  # Set to store used session IDs
        _lock = None  # Lock for thread-safe ID generation

        @classmethod
        def generate(cls, session) -> str: 
            """
            Generate a unique session ID.
            """
            session_id = uuid4()
            while session_id in cls._ids:
                session_id = uuid4()
            cls._ids[session_id] = session
            return session_id
            
    
    class SessionStatus(Enum):
        """
        Enum-like class to represent the status of a session.
        """
        INITIALIZED, RUNNING, PAUSED, TERMINATED, STOPPED, ERROR = range(6)

    def __init__(self, name: str):
        self.id = Session.SessionID.generate(self)
        self.name = name
        self.thread = None
        self.status = self.SessionStatus.INITIALIZED
        self._lock = None
        self._shutdown = False

class TRNXSession(Session):
    """
    Class to manage a TRNX session.
    """

    def __init__(self, name: str, trnx: TRNX = None):
        super().__init__(name)
        self.trnx = None

class FactorySession(Session):
    """
    Class to manage a TRNX factory session, including its configuration and status.
    """

    def __init__(self, name: str, trnx_editor: TRNXEditor = None):
        super().__init__(name)
        self.trnx_editor = None

