from typing import Dict, Tuple, List, Optional
from uuid import UUID
from enum import Enum

from .session import Session, TRNXSession, CanvasSession


class SessionManager:

    class SessionType(Enum):
        TRNX = TRNXSession
        CANVAS = CanvasSession

    def __init__(self):
        # Storage for multiple sessions of each type
        self._canvas_sess: Dict[UUID, CanvasSession] = {}
        self._trnx_sess: Dict[UUID, TRNXSession] = {}

    # ----------------------
    # Canvas (Editor) Sessions
    # ----------------------

    def start_new_canvas_session(self, name: str, *args, **kwargs) -> Tuple[UUID, CanvasSession]:
        if any(sess.name == name for sess in self._canvas_sess.values()):
            raise ValueError(f"Canvas session '{name}' already exists.")
        session = CanvasSession(name, *args, **kwargs)
        self._canvas_sess[session.id] = session
        return session.id, session

    # ----------------------
    # TRNX (Runtime) Sessions
    # ----------------------

    def start_new_trnx_session(self, name: str, *args, **kwargs) -> Tuple[UUID, TRNXSession]:
        if any(sess.name == name for sess in self._trnx_sess.values()):
            raise ValueError(f"TRNX session '{name}' already exists.")
        session = TRNXSession(name, *args, **kwargs)
        self._trnx_sess[session.id] = session
        return session.id, session

    # ----------------------
    # Session Retrieval
    # ----------------------

    def retrieve_session_by_id(self, sess_id: UUID, sess_type: "SessionManager.SessionType" = None) -> Optional[Session]:
        if sess_type == self.SessionType.CANVAS:
            return self._canvas_sess.get(sess_id)
        elif sess_type == self.SessionType.TRNX:
            return self._trnx_sess.get(sess_id)
        else:
            return self._canvas_sess.get(sess_id) or self._trnx_sess.get(sess_id)

    def retrieve_session_by_name(self, name: str, sess_type: "SessionManager.SessionType" = None) -> Session:
        if sess_type == self.SessionType.CANVAS or sess_type is None:
            for session in self._canvas_sess.values():
                if session.name == name:
                    return session
        if sess_type == self.SessionType.TRNX or sess_type is None:
            for session in self._trnx_sess.values():
                if session.name == name:
                    return session
        raise KeyError(f"Session with name '{name}' not found.")

    # ----------------------
    # Convenience Accessors
    # ----------------------

    @property
    def canvases(self) -> Dict[UUID, CanvasSession]:
        return self._canvas_sess

    @property
    def trnxs(self) -> Dict[UUID, TRNXSession]:
        return self._trnx_sess

    @property
    def sessions(self) -> List[Session]:
        return list(self._canvas_sess.values()) + list(self._trnx_sess.values())
