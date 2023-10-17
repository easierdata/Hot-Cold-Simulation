import logging
from typing import Optional

from modules.config import MONTE_CARLO_LOG_DIR  # type: ignore


def setup_logger(logger_name: Optional[str] = "logger") -> logging.Logger:
    """_summary_

    Args:
        logger_name (Optional[str], optional): _description_. Defaults to "logger".

    Returns:
        logging.Logger: _description_
    """
    # Create and configure a custom logger
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(message)s")

    # Create handlers
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler((MONTE_CARLO_LOG_DIR / "results.log").as_posix())
    file_handler.setFormatter(formatter)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
