from dataclasses import dataclass, field
from typing import Dict, Tuple, Any
import numpy as np

# TODO: Add type hints to the methods and parameters.
# TODO: Split by inheriting Parameters into seperate classes for static and dynamic variables.

class Param:
    """
    Represents an individual parameter.
    
    Attributes:
      - name: Name of the parameter.
      - dtype: Data type (e.g. int, float).
      - allowed_range: Optional tuple (min, max) for a continuous range.
      - allowed_values: Optional list of discrete allowed values.
      - default_value: Default value.
      - description: Description of the parameter.
    """
    def __init__(self, name: str, dtype: Any, default_value: Any = None,
                 allowed_range: Tuple[Any, Any] = None, allowed_values: list = None,
                 description: str = ""):
        self.name = name
        self.dtype = dtype
        self.allowed_range = allowed_range
        self.allowed_values = allowed_values
        self.default_value = default_value
        self.description = description
        self.value = default_value

class Parameters:
    """
    Holds individual parameters as attributes.
    Use add_param() to add a parameter. They can then be accessed as attributes.
    """
    def __init__(self):
        pass

    def add_param(self, param: Param) -> None:
        setattr(self, param.name, param)

    def get(self, name: str) -> Any:
        param = getattr(self, name, None)
        if param is not None:
            return param.default_value
        else:
            raise KeyError(f"Parameter '{name}' not found.")

    def update(self, name: str, value: Any) -> None:
        param = getattr(self, name, None)
        if param is not None:
            param.default_value = value
        else:
            raise KeyError(f"Parameter '{name}' not found.")

    def __repr__(self) -> str:
        # Return only the user-added parameters (ignore private attributes)
        params = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return f"Parameters({params})"


class NodeConfig:
    """
    Base configuration for a node.
    Contains:
      - parameters: Dynamic and static parameters (as attributes).
      - inputs: Expected input ports, mapping port name to (shape, dtype).
      - outputs: Expected output ports, mapping port name to (shape, dtype).
    """
    def __init__(self):
        self.parameters = Parameters()
        self.inputs: Dict[str, Tuple[Tuple[int, ...], Any]] = {}
        self.outputs: Dict[str, Tuple[Tuple[int, ...], Any]] = {}

    def update_io(self) -> None:
        """
        Update the input and output definitions based on the current static parameters.
        This should be overridden in derived configuration classes.
        """
        raise NotImplementedError("update_io() must be implemented in derived NodeConfig classes.")