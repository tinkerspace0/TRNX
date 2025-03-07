import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    """Centralized logger for the application with file and console output."""

    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    
    @classmethod
    def _setup(cls):
        """Sets up the logger with file rotation and console logging."""
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)  # Ensure log directory exists

        logger = logging.getLogger("TrenexLogger")
        logger.setLevel(logging.DEBUG)  # Capture all levels

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File Handler with Rotation (5 files of 1MB each)
        file_handler = RotatingFileHandler(cls.LOG_FILE, maxBytes=1_000_000, backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    @classmethod
    def get_logger(cls):
        """Returns a configured logger instance."""
        if not hasattr(cls, "_logger"):
            cls._logger = cls._setup()
        return cls._logger

# Global logger instance
logger = Logger.get_logger()
