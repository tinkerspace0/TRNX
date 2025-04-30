# core/controller/controller.py

from enum import Enum
from typing import Tuple
from uuid import UUID

from core.debug.logger import gl_logger
from core.session import SessionManager
from core.node.manager import NodeManager


class TrenexController:
    """
    TrenexController is the central backend application.
    It holds the SessionManager and NodeManager, and orchestrates
    core operations for the Trenex system.
    """


    def __init__(self):
        self.name = "Trenex"
        self._nm: NodeManager = NodeManager()
        self._ssm: SessionManager = SessionManager()
        
        gl_logger.info(f"TrenexController initialized.")
