import logging
import os

def setup_logger():
    # Create and configure a custom logger
    logger = logging.getLogger('monte_carlo_logger')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter('%(message)s')

    # Create handlers
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(os.path.join(os.getcwd(), 'monte_carlo_results', 'results.log'))
    file_handler.setFormatter(formatter)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
