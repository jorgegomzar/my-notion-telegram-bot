import logging


def get_logger(logger_name: str):
    """Defines logging handlers and format.

    Returns logger object.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(logger_name)
    return logger
