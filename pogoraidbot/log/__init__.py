import logging
from typing import Union

PACKAGE_LOGGERS = [
    "pogoraidbot.bot",
    "pogoraidbot.screenshot",
    "pogoraidbot.data.data",
    "pogoraidbot.data.gym",
    "pogoraidbot.data.boss"
]


def logger_setup(log_level: Union[int, str] = logging.ERROR, modules_log_level: int = logging.ERROR):
    # Set format for the log
    logging.basicConfig(format="%(levelname)s|%(name)s|%(message)s", level=modules_log_level)

    for l in PACKAGE_LOGGERS:
        logging.getLogger(l).setLevel(log_level)
