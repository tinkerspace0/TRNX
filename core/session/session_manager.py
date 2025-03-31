from typing import Dict, Tuple
from uuid import UUID
from enum import Enum

from .session import Session, TRNXSession, FactorySession

class SessionManager:

    class SessionType(Enum):
        TRNX = TRNXSession
        FACTORY = FactorySession

    def __init__(self):
        # Use separate storage dictionaries for each session type.
        self._proj_sess: Dict[UUID, Session] = {}  # For FactorySession (projects)
        self._trnx_sess: Dict[UUID, Session] = {}   # For TRNXSession (runtime)

    def _get_storage(self, session_type: "SessionManager.SessionType") -> Dict[UUID, Session]:
        if session_type == self.SessionType.FACTORY:
            return self._proj_sess
        elif session_type == self.SessionType.TRNX:
            return self._trnx_sess
        else:
            raise ValueError("Unsupported session type.")

    def start_new_session(self, name: str, session_type: "SessionManager.SessionType", *args, **kwargs) -> Tuple[UUID, Session]:
        storage = self._get_storage(session_type)
        # Check if a session with this name already exists in the chosen storage.
        if any(session.name == name for session in storage.values()):
            raise ValueError(f"Session with name {name} already exists.")
        session_class = session_type.value
        if not issubclass(session_class, Session):
            raise ValueError("Provided session type does not subclass Session.")
        session = session_class(name, *args, **kwargs)
        storage[session.id] = session
        return (session.id, session)
    
    def ret_sess_bid(self, sess_id: UUID, sess_type: "SessionManager.SessionType" = None) -> Session:
        if sess_type:
            storage = self._get_storage(sess_type)
            return storage.get(sess_id)
        else:
            # Search both dictionaries.
            session = self._proj_sess.get(sess_id)
            if session:
                return session
            return self._trnx_sess.get(sess_id)

    def ret_sess_bname(self, name: str, sess_type: "SessionManager.SessionType" = None) -> Session:
        if sess_type:
            storage = self._get_storage(sess_type)
            for session in storage.values():
                if session.name == name:
                    return session
            raise KeyError(f"Session with name {name} not found.")
        else:
            for session in list(self._proj_sess.values()) + list(self._trnx_sess.values()):
                if session.name == name:
                    return session
            raise KeyError(f"Session with name {name} not found.")

    @property
    def all_sessions(self):
        # Combine sessions from both storage dictionaries.
        all_sessions = list(self._proj_sess.values()) + list(self._trnx_sess.values())
        return [
            {
                "id": str(session.id),
                "name": session.name,
                "status": session.status.name.lower(),
                "type": session.type.name.lower() if session.type is not None else "unknown"
            }
            for session in all_sessions
        ]