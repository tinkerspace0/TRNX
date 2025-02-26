import uuid
from typing import Set

class GlobalIDGenerator:
    """
    A 'static' or 'global' ID generator using class variables.
    This version checks for collisions both on generation and on registration.
    """

    _generated_ids: Set[str] = set()

    @classmethod
    def generate_id(cls) -> str:
        """
        Generate a new UUID4 and store it in the class-level set, ensuring no duplicates.
        """
        while True:
            new_id = str(uuid.uuid4())
            if new_id not in cls._generated_ids:
                cls._generated_ids.add(new_id)
                return new_id
            # If there's a collision, keep generating until you find a unique one.

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
