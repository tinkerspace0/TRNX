import uuid
import hashlib
from typing import Set
from core.debug.logger import logger  
from core.debug.profiler import Profiler

class IDGenerator:
    """
    A 'static' or 'global' ID generator using class variables.
    This version checks for collisions both on generation and on registration.
    """

    _generated_ids: Set[str] = set()

    @classmethod
    @Profiler.profile
    def generate_id(cls) -> str:
        """
        Generate a new short unique ID, ensuring no duplicates.
        """
        while True:
            new_id = uuid.uuid4().hex[:10]  # Convert to hex and truncate to 10 chars
            if new_id not in cls._generated_ids:
                cls._generated_ids.add(new_id)
                logger.debug(f"Generated new unique ID: {new_id}")
                return new_id
            logger.warning(f"ID collision detected for {new_id}, retrying...")

    @classmethod
    @Profiler.profile
    def has_id(cls, identity: str) -> bool:
        """Check if an ID has already been generated."""
        exists = identity in cls._generated_ids
        logger.debug(f"Checked existence of ID '{identity}': {'Exists' if exists else 'Does not exist'}")
        return exists

    @classmethod
    @Profiler.profile
    def register_id(cls, identity: str) -> None:
        """
        Register an externally provided ID into the generator's set.
        Raises a ValueError if the ID is already in use.
        """
        if identity in cls._generated_ids:
            logger.error(f"Attempted to register duplicate ID: {identity}")
            raise ValueError(f"ID '{identity}' is already registered.")

        cls._generated_ids.add(identity)
        logger.info(f"Registered new ID: {identity}")
