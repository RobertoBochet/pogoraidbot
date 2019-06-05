#!/usr/bin/env python3
import logging
import os
import sys

from bot import PoGORaidBot

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        bot = PoGORaidBot(os.environ["BOT_TOKEN"])
    except KeyError:
        logging.fatal("Bot token not found")
        sys.exit(1)

    bot.listen()
