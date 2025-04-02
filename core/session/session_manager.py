from typing import Dict, Tuple
from uuid import UUID
from enum import Enum

from .session import Session, TRNXSession, FactorySession

class SessionManager:

    class SessionType(Enum):
        TRNX = TRNXSession
        FACTORY = FactorySession

    def __init__(self):
        # Only one factory session (project) is allowed.
        self._proj_sess: FactorySession = None
        # Multiple TRNX sessions (runtime) can be created.
        self._trnx_sess: Dict[UUID, TRNXSession] = {}


    # Create a new project (factory session)
    def start_new_project(self, name: str, *args, **kwargs) -> FactorySession:
        if self._proj_sess is not None:
            raise ValueError(f"A project already exists with name '{self._proj_sess.name}'.")
        # Create a FactorySession
        session = FactorySession(name, *args, **kwargs)
        self._proj_sess = session
        return session

    # Create a new TRNX session (runtime)
    def start_new_trnx_session(self, name: str, *args, **kwargs) -> Tuple[UUID, TRNXSession]:
        if any(session.name == name for session in self._trnx_sess.values()):
            raise ValueError(f"Session with name {name} already exists.")
        session = TRNXSession(name, *args, **kwargs)
        self._trnx_sess[session.id] = session
        return (session.id, session)


    # Retrieve session by ID: if sess_type provided, look in that storage; otherwise, search both.
    def retrieve_session_by_id(self, sess_id: UUID, sess_type: "SessionManager.SessionType" = None) -> Session:
        if sess_type:
            if sess_type == self.SessionType.FACTORY:
                return self._proj_sess if self._proj_sess and self._proj_sess.id == sess_id else None
            elif sess_type == self.SessionType.TRNX:
                return self._trnx_sess.get(sess_id)
        else:
            # Check factory session first
            if self._proj_sess and self._proj_sess.id == sess_id:
                return self._proj_sess
            return self._trnx_sess.get(sess_id)

    def retrieve_session_by_name(self, name: str, sess_type: "SessionManager.SessionType" = None) -> Session:
        if sess_type:
            if sess_type == self.SessionType.FACTORY:
                if self._proj_sess and self._proj_sess.name == name:
                    return self._proj_sess
                raise KeyError(f"Project with name {name} not found.")
            elif sess_type == self.SessionType.TRNX:
                for session in self._trnx_sess.values():
                    if session.name == name:
                        return session
                raise KeyError(f"TRNX session with name {name} not found.")
        else:
            if self._proj_sess and self._proj_sess.name == name:
                return self._proj_sess
            for session in self._trnx_sess.values():
                if session.name == name:
                    return session
            raise KeyError(f"Session with name {name} not found.")

    @property
    def project(self):
        return self._proj_sess

    @property
    def trnxs(self):
        return self._trnx_sess
    
    @property
    def sessions(self):
        sessions = []
        if self._proj_sess is not None:
            sessions.append(self._proj_sess)
        sessions.extend(self._trnx_sess.values())
        return sessions