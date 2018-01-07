import logging


def enable_logging(logger_name=__name__, level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
