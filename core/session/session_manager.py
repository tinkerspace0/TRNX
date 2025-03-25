from typing import Dict, Tuple
from uuid import uuid4, UUID
from enum import Enum

from .session import Session, TRNXSession, FactorySession



class SessionManager:

    class SessionType(Enum):
        TRNX = TRNXSession
        FACTORY = FactorySession

    def __init__(self):
        self._sessions: Dict[UUID, Session] = {}

    def start_new_session(self, name: str, session_type: SessionType, *args, **kwargs) -> Tuple[UUID, str]:
        if session_type not in self.SessionType:
            raise ValueError(f"Invalid session type: {session_type}")
        if name in self.all_sessions:
            raise ValueError(f"Session with name {name} already exists.")

        session_class = session_type.value
        if isinstance(session_class, Session):
            session = session_class(name, *args, **kwargs)
        session = session_class(name, *args, **kwargs)

        self._sessions[session.id] = session
        return [session.id, session.name]
    
    def retrieve_session_by_id(self, session_id: UUID) -> Session:
        return self._sessions.get(session_id)

    def retrieve_session_by_name(self, name: str) -> Session:
        for session in self._sessions.values():
            if session.name == name:
                return session
        raise KeyError(f"Session with name {name} not found.")

    @property
    def all_sessions(self):
        return [session.name for session in self._sessions.values()]

    # @property
    # def active_sessions(self):
    #     return [session.name for session in self._sessions.values() if session.status == Session.SessionStatus.RUNNING]
    
    # @property
    # def paused_sessions(self):
    #     return [session.name for session in self._sessions.values() if session.status == Session.SessionStatus.PAUSED]
    
    # @property
    # def stopped_sessions(self):
    #     return [session.name for session in self._sessions.values() if session.status == Session.SessionStatus.STOPPED]
  
    # @property
    # def error_sessions(self):
    #     return [session.name for session in self._sessions.values() if session.status == Session.SessionStatus.ERROR]
  
