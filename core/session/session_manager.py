
# session_manager.py
from typing import Dict, Tuple, Optional
from uuid import UUID
from .session import Session

class SessionManager:
    """
    Manages TRNX sessions using the unified Session class.
    """
    def __init__(self):
        self._sessions: Dict[UUID, Session] = {}

    def start_new_session(self, name: str) -> Tuple[UUID, Session]:
        """
        Create and store a new Session with the given name.
        Raises ValueError if a session with the same name exists.
        """
        if any(sess.name == name for sess in self._sessions.values()):
            raise ValueError(f"Session '{name}' already exists.")
        session = Session(name)
        self._sessions[session.id] = session
        return session.id, session

    def retrieve_session_by_id(self, sess_id: UUID) -> Optional[Session]:
        """
        Retrieve a session by its UUID.
        Returns None if not found.
        """
        return self._sessions.get(sess_id)

    def retrieve_session_by_name(self, name: str) -> Session:
        """
        Retrieve a session by its name.
        Raises KeyError if not found.
        """
        for session in self._sessions.values():
            if session.name == name:
                return session
        raise KeyError(f"Session with name '{name}' not found.")

    @property
    def sessions(self) -> Dict[UUID, Session]:
        """
        Returns all active sessions.
        """
        return dict(self._sessions)
