import logging
import sys


def enable_logging(logger_name=__name__, level=logging.DEBUG):
    logging.basicConfig(level=level,
                        stream=sys.stdout,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(logger_name)
    # logger.setLevel(level)
    return logger
