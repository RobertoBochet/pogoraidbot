#!/usr/bin/env python3
import logging
import os
import argparse

from bot import PoGORaidBot

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s|%(name)s|%(message)s")

    # Set warning logging level for the module
    logging.getLogger("bot").setLevel(logging.DEBUG)
    logging.getLogger("screenshot").setLevel(logging.DEBUG)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)

    # Get environment variables
    env = {}

    env["token"] = os.getenv("BOT_TOKEN")
    env["host"] = os.getenv("REDIS_HOST")
    env["port"] = os.getenv("REDIS_PORT")
    env["debug_folder"] = os.getenv("DEBUG_FOLDER")

    # Get inline arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--token", dest="token", help="telegram bot token")
    parser.add_argument("-r", "--host", dest="host", help="redis host")
    parser.add_argument("-p", "--port", dest="port", help="redis port")
    parser.add_argument("-d", "--debug-folder", dest="debug_folder", help="debug folder")

    args = vars(parser.parse_args())

    # Remove None elements
    env = {k: env[k] for k in env if env[k] is not None}
    args = {k: args[k] for k in args if args[k] is not None}

    # Merge environment variables and inline arguments
    args = {**env, **args}

    # Create the bot
    bot = PoGORaidBot(**args)

    # Manage updates
    bot.listen()
