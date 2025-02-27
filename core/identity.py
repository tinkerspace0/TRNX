import uuid
import hashlib
from typing import Set

class IDGenerator:
    """
    A 'static' or 'global' ID generator using class variables.
    This version checks for collisions both on generation and on registration.
    """

    _generated_ids: Set[str] = set()

    @classmethod
    def generate_id(cls) -> str:
        """
        Generate a new short unique ID, ensuring no duplicates.
        """
        while True:
            # Generate a UUID4 and take only the first 10 characters
            new_id = uuid.uuid4().hex[:10]  # Convert to hex and truncate to 10 chars
            if new_id not in cls._generated_ids:
                cls._generated_ids.add(new_id)
                return new_id

    @classmethod
    def has_id(cls, identity: str) -> bool:
        """Check if an ID has already been generated."""
        return identity in cls._generated_ids

    @classmethod
    def register_id(cls, identity: str) -> None:
        """
        Register an externally provided ID into the generator's set.
        Raises a ValueError if the ID is already in use.
        """
        if identity in cls._generated_ids:
            raise ValueError(f"ID '{identity}' is already registered.")
        cls._generated_ids.add(identity)
