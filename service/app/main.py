#!/usr/bin/env python3
import logging
import os

from bot import PoGORaidBot

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,format="%(levelname)s|%(name)s|%(message)s")

    # Set warning logging level for the module
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("JobQueue").setLevel(logging.WARNING)

    env = {"token": "BOT_TOKEN", "host": "REDIS_HOST", "port": "REDIS_PORT"}
    env = {k: os.environ[env[k]] for k in env if env[k] in os.environ}

    bot = PoGORaidBot(**env)

    bot.listen()
