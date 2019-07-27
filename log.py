import logging


def intial_setup():
    # Set format for the log
    logging.basicConfig(format="%(levelname)s|%(name)s|%(message)s")


def setup_log_levels(log_level: int, modules_log_level: int = logging.ERROR):
    # Set log level for application logger
    logging.getLogger("bot").setLevel(log_level)
    logging.getLogger("screenshot").setLevel(log_level)
    logging.getLogger("gym").setLevel(log_level)

    # Set log level for modules
    logging.getLogger("telegram").setLevel(modules_log_level)
    logging.getLogger("telegram.ext.dispatcher").setLevel(modules_log_level)
    logging.getLogger("telegram.ext.updater").setLevel(modules_log_level)
    logging.getLogger("JobQueue").setLevel(modules_log_level)
