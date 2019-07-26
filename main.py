#!/usr/bin/env python3
import argparse
import logging
import os

from bot import PoGORaidBot

if __name__ == "__main__":
    # Set logging format
    logging.basicConfig(format="%(levelname)s|%(name)s|%(message)s")

    # Get environment variables
    env = {}

    env["token"] = os.getenv("BOT_TOKEN")
    env["host"] = os.getenv("REDIS_HOST")
    env["port"] = os.getenv("REDIS_PORT")
    env["superadmin"] = os.getenv("SUPERADMIN")
    env["gyms_file"] = os.getenv("GYMS_FILE")
    env["debug_folder"] = os.getenv("DEBUG_FOLDER")
    env["verbosity_level"] = os.getenv("VERBOSITY_LEVEL")

    # Get inline arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--token", dest="token", help="telegram bot token")
    parser.add_argument("-r", "--host", dest="host", help="redis host")
    parser.add_argument("-p", "--port", dest="port", help="redis port")
    parser.add_argument("-a", "--superadmin", dest="superadmin", help="superadmin's id")
    parser.add_argument("-g", "--gyms-file", dest="gyms_file",
                        help="JSON file contains gyms and their coordinates. It can be also provided with http(s)")
    parser.add_argument("-d", "--debug-folder", dest="debug_folder", help="debug folder")
    parser.add_argument("-v", dest="verbosity_level", action="count", default=None,
                        help="number of -v specifics level of verbosity")
    parser.add_argument("--verbose", dest="verbosity_level", action="store_const", const=3,
                        help="equal to -vvv")
    parser.add_argument("--debug", dest="verbosity_level", action="store_const", const=4,
                        help="equal to -vvvv")

    args = vars(parser.parse_args())

    # Remove None elements
    env = {k: env[k] for k in env if env[k] is not None}
    args = {k: args[k] for k in args if args[k] is not None}

    # Merge environment variables and inline arguments
    args = {**env, **args}

    # Found verbosity level
    try:
        v = args.pop("verbosity_level")

        if isinstance(v, int) and v >= 4:
            v = 4

        if v == "DEBUG" or v == 4:
            verbosity_level = logging.DEBUG
        elif v == "VERBOSE" or v == 3:
            verbosity_level = logging.VERBOSE
        elif v == "INFO" or v == 2:
            verbosity_level = logging.INFO
        elif v == "WARNING" or v == 1:
            verbosity_level = logging.WARNING
        elif v == "ERROR":
            verbosity_level = logging.ERROR
    except KeyError:
        verbosity_level = logging.ERROR

    # Set warning logging level for the module
    logging.getLogger("bot").setLevel(verbosity_level)
    logging.getLogger("screenshot").setLevel(verbosity_level)
    logging.getLogger("gym").setLevel(verbosity_level)
    logging.getLogger("telegram").setLevel(logging.ERROR)
    logging.getLogger("telegram.ext.dispatcher").setLevel(logging.ERROR)
    logging.getLogger("telegram.ext.updater").setLevel(logging.ERROR)
    logging.getLogger("JobQueue").setLevel(logging.ERROR)

    # Create the bot
    bot = PoGORaidBot(**args)

    # Manage updates
    bot.listen()
