import time
import functools
import json
import os
from core.debug.logger import logger

class Profiler:
    """
    A simple profiler to measure execution time of functions or code blocks.
    - Logs to console, `logs/profiler.log`, and `logs/profiler.json`
    - Use as a decorator: `@Profiler.profile`
    - Use as a context manager: `with Profiler()`
    """

    JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs/profiler.json")

    def __init__(self, name="Code Block"):
        self.name = name
        self.start_time = None

    def __enter__(self):
        """Start profiling when entering the context."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop profiling and log execution time when exiting the context."""
        elapsed_time = time.perf_counter() - self.start_time
        log_entry = {"name": self.name, "execution_time": round(elapsed_time, 6)}
        
        logger.info(f"[Profiler] {self.name} executed in {elapsed_time:.6f} seconds.")
        self._write_to_json(log_entry)

    @staticmethod
    def profile(func):
        """
        Decorator to measure execution time of a function.
        Example:
            @Profiler.profile
            def some_function():
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            
            log_entry = {"name": func.__name__, "execution_time": round(elapsed_time, 6)}
            logger.info(f"[Profiler] Function '{func.__name__}' executed in {elapsed_time:.6f} seconds.")
            Profiler._write_to_json(log_entry)
            
            return result
        return wrapper

    @staticmethod
    def _write_to_json(log_entry):
        """Write execution time logs to a JSON file."""
        if not os.path.exists(os.path.dirname(Profiler.JSON_FILE)):
            os.makedirs(os.path.dirname(Profiler.JSON_FILE))

        try:
            if os.path.exists(Profiler.JSON_FILE):
                with open(Profiler.JSON_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = []

            data.append(log_entry)  # Append new profiling entry

            with open(Profiler.JSON_FILE, "w") as f:
                json.dump(data, f, indent=4)  # Write back updated log
        except Exception as e:
            logger.error(f"[Profiler] Failed to write to JSON: {e}")
