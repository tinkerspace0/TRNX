from typing import Dict, Tuple
from uuid import UUID
from enum import Enum

from .session import Session, TRNXSession, FactorySession

class SessionManager:

    class SessionType(Enum):
        TRNX = TRNXSession
        FACTORY = FactorySession

    def __init__(self):
        self._sessions: Dict[UUID, Session] = {}

    def start_new_session(self, name: str, session_type: "SessionManager.SessionType", *args, **kwargs) -> Tuple[UUID, Session]:
        # Check if a session with this name already exists.
        if any(session.name == name for session in self._sessions.values()):
            raise ValueError(f"Session with name {name} already exists.")

        session_class = session_type.value
        # Check that session_class is a subclass of Session.
        if not issubclass(session_class, Session):
            raise ValueError("Provided session type does not subclass Session.")
        session = session_class(name, *args, **kwargs)
        self._sessions[session.id] = session
        return (session.id, session)

    def retrieve_session_by_id(self, session_id: UUID) -> Session:
        return self._sessions.get(session_id)

    def retrieve_session_by_name(self, name: str) -> Session:
        for session in self._sessions.values():
            if session.name == name:
                return session
        raise KeyError(f"Session with name {name} not found.")

    @property
    def all_sessions(self):
        # Return a list of dictionaries with session details.
        return [
            {"id": str(session.id), "name": session.name, "status": session.status.name}
            for session in self._sessions.values()
        ]
