__all__ = ["LoggerSetup"]

import logging
from typing import Union, List

VERBOSITY_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}

class LoggerSetup:
    def __init__(self,loggers: List[str], log_level: Union[int, str], modules_log_level: Union[int, str] = logging.ERROR):
        if isinstance(log_level, str):
            log_level = VERBOSITY_LEVELS[log_level]

        if isinstance(modules_log_level, str):
            modules_log_level = VERBOSITY_LEVELS[modules_log_level]

        # Set format for the log
        logging.basicConfig(format="%(levelname)s|%(name)s|%(message)s", level=modules_log_level)

        for l in loggers:
            logging.getLogger(l).setLevel(log_level)
