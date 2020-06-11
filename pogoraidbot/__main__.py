#!/usr/bin/env python3
import argparse
import logging
import os

from pogoraidbot import PoGORaidBot
from .log import logger_setup

if __name__ == "__main__":
    # Gets inline arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--token", dest="token", help="telegram bot token")
    parser.add_argument("-r", "--redis", dest="redis", help="redis url in \"redis://{host}[:port]/{db}\" format")
    parser.add_argument("-a", "--superadmin", dest="superadmin", help="superadmin's id")
    parser.add_argument("-b", "--bosses-file", dest="bosses_file",
                        help="JSON or CSV file contains possible pokémons in the raids. It can be also provided over http(s)")
    parser.add_argument("-o", "--bosses-expiration", dest="bosses_expiration",
                        help="Validity of the bosses list in hours")
    parser.add_argument("-g", "--gyms-file", dest="gyms_file",
                        help="JSON file contains gyms and their coordinates. It can be also provided over http(s)")
    parser.add_argument("-y", "--gyms-expiration", dest="gyms_expiration",
                        help="Validity of the gyms list in hours")
    parser.add_argument("-e", "--env", dest="env", action="store_true",
                        help="Use environment variables for the configuration")
    parser.add_argument("-d", "--debug-folder", dest="debug_folder", help="debug folder")
    parser.add_argument("-v", dest="log_level", action="count",
                        help="number of -v specifics level of verbosity")
    parser.add_argument("--info", dest="log_level", action="store_const", const=2, help="equal to -vv")
    parser.add_argument("--debug", dest="log_level", action="store_const", const=3, help="equal to -vvv")

    # Parses args
    args = vars(parser.parse_args())

    # Removes None elements
    args = {k: args[k] for k in args if args[k] is not None}

    if args["env"]:
        env = {
            "token": os.getenv("PGRB_BOT_TOKEN"),
            "redis": os.getenv("PGRB_BOT_REDIS"),
            "superadmin": os.getenv("PGRB_BOT_SUPERADMIN"),
            "gyms_file": os.getenv("PGRB_BOT_GYMS_FILE"),
            "gyms_expiration": os.getenv("PGRB_BOT_GYMS_EXPIRATION"),
            "bosses_file": os.getenv("PGRB_BOT_BOSSES_FILE"),
            "bosses_expiration": os.getenv("PGRB_BOT_BOSSES_EXPIRATION"),
            "log_level": os.getenv("PGRB_BOT_LOG_LEVEL")
        }

        if os.getenv("PGRB_BOT_DEBUG_PATH") is not None:
            env["debug_folder"] = "/srv"

        # Removes None elements
        env = {k: env[k] for k in env if env[k] is not None}

        args = {**env, **args}

    del args["env"]

    # Parses the verbosity level
    try:
        logger_setup({
                         0: logging.ERROR,
                         1: logging.WARNING,
                         2: logging.INFO,
                         3: logging.DEBUG,
                         "ERROR": logging.ERROR,
                         "WARNING": logging.WARNING,
                         "INFO": logging.INFO,
                         "DEBUG": logging.DEBUG
                     }[args["log_level"]])

    except KeyError:
        logger_setup()

    if "log_level" in args:
        del args["log_level"]

    # Creates the bot
    bot = PoGORaidBot(**args)

    # Manages updates
    bot.listen()
