import logging
from typing import Optional


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Set up and configure a logger.

    Args:
        name: Logger name
        level: Optional logging level

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Set level if provided, otherwise use INFO
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)

    # Only add handler if none exists to avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
