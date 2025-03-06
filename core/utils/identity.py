import uuid
import hashlib
from typing import Dict, Any, Optional
from trenex.core.debug.logger import logger  
from trenex.core.debug.profiler import Profiler

class IDGenerator:
    """
    A global ID generator for creating unique identifiers.
    This generator checks for collisions and stores a mapping from IDs to objects.
    """

    _generated_ids: Dict[str, Any] = {}  # Stores mapping from generated IDs to objects.

    @classmethod
    @Profiler.profile
    def generate_id(cls, id_object: Any = None) -> str:
        """
        Generate a new short unique ID, ensuring no duplicates, and associate it with id_object if provided.

        Args:
            id_object (Any, optional): The object to associate with the generated ID. Defaults to None.

        Returns:
            str: A unique identifier.
        """
        while True:
            new_id = uuid.uuid4().hex[:10]  # Generate a UUID4, take the first 10 hex characters.
            if new_id not in cls._generated_ids:
                cls._generated_ids[new_id] = id_object  # Associate the object with the new ID.
                logger.debug(f"Generated new unique ID: {new_id}")
                return new_id
            logger.warning(f"ID collision detected for {new_id}, retrying...")

    @classmethod
    @Profiler.profile
    def get_object_with_id(cls, identity: str) -> Optional[Any]:
        """
        Retrieve the object associated with the given ID.

        Args:
            identity (str): The ID to look up.

        Returns:
            Optional[Any]: The associated object if found, otherwise None.
        """
        return cls._generated_ids.get(identity)
    
    @classmethod
    @Profiler.profile
    def has_id(cls, identity: str) -> bool:
        """
        Check if an ID has already been generated.

        Args:
            identity (str): The ID to check.

        Returns:
            bool: True if the ID exists, False otherwise.
        """
        exists = identity in cls._generated_ids
        logger.debug(f"Checked existence of ID '{identity}': {'Exists' if exists else 'Does not exist'}")
        return exists

    @classmethod
    @Profiler.profile
    def register_id(cls, identity: str, id_object: Any) -> None:
        """
        Register an externally provided ID into the generator's mapping.
        Raises a ValueError if the ID is already registered.

        Args:
            identity (str): The externally provided ID.
            id_object (Any): The object to associate with the provided ID.
        
        Raises:
            ValueError: If the ID is already registered.
        """
        if identity in cls._generated_ids:
            logger.error(f"Attempted to register duplicate ID: {identity}")
            raise ValueError(f"ID '{identity}' is already registered.")

        cls._generated_ids[identity] = id_object
        logger.info(f"Registered new ID: {identity}")
