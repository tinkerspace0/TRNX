# session.py
from uuid import uuid4, UUID
from threading import Thread
from enum import Enum
from core.trnx import TRNX

class Session:
    """
    A simple TRNX session manager without subclasses.
    """
    class SessionID:
        _ids = set()

        @classmethod
        def generate(cls) -> UUID:
            sess_id = uuid4()
            while sess_id in cls._ids:
                sess_id = uuid4()
            cls._ids.add(sess_id)
            return sess_id

    class Status(Enum):
        INITIALIZED = 0
        STARTING = 1
        RUNNING = 2
        PAUSED = 3
        STOPPING = 4
        TERMINATED = 5
        ERROR = 6

    def __init__(self, name: str):
        self.id: UUID = Session.SessionID.generate()
        self.name = name
        self.status = self.Status.TERMINATED
        self._thread = None
        self._shutdown = False
        self.worker: TRNX = None

    def load_worker(self, worker: TRNX):
        if not isinstance(worker, TRNX):
            raise TypeError("Worker must be a TRNX instance")
        self.worker = worker
        self.status = self.Status.INITIALIZED

    def start(self):
        if self.worker is None:
            raise ValueError("No TRNX worker attached.")
        self.status = self.Status.STARTING
        if self._thread is None or not self._thread.is_alive():
            self.worker._stop = False
            self._thread = Thread(target=self.worker.run, daemon=True)
            self._thread.start()
            self.status = self.Status.RUNNING

    def stop(self, timeout: int = 5):
        self.status = self.Status.STOPPING
        if self._thread and self._thread.is_alive():
            self.worker._stop = True
            self._thread.join(timeout=timeout)
        self.status = self.Status.TERMINATED
