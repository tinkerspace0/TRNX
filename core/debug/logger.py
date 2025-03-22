import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    """Centralized logger with global and custom logging options."""

    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
    DEFAULT_LOG_FILE = "app.log"
    
    @classmethod
    def _setup(cls, log_file):
        """Sets up a logger with file rotation and console logging."""
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)  # Ensure log directory exists

        logger = logging.getLogger(log_file)
        logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Avoid adding multiple handlers to the same logger
        if logger.hasHandlers():
            return logger

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File Handler with Rotation
        log_path = os.path.join(cls.LOG_DIR, log_file)
        file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    @classmethod
    def get_logger(cls, log_file=None):
        """Returns a configured logger instance.
        - If log_file is None, returns the global logger.
        - Otherwise, returns a separate logger with the given log file name.
        """
        if log_file is None:
            log_file = cls.DEFAULT_LOG_FILE
            if not hasattr(cls, "_global_logger"):
                cls._global_logger = cls._setup(log_file)
            return cls._global_logger
        else:
            return cls._setup(log_file)

# Global logger instance
gl_logger = Logger.get_logger()
