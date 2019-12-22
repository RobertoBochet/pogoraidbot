#!/usr/bin/env python3
import os
from bot import PoGORaidBot

if __name__ == "__main__":

    # Get environment variables
    env = {}

    env["token"] = os.getenv("PGRB_BOT_TOKEN")
    env["host"] = os.getenv("PGRB_REDIS_HOST")
    env["port"] = os.getenv("PGRB_REDIS_PORT")
    env["superadmin"] = os.getenv("PGRB_BOT_SUPERADMIN")
    env["gyms_file"] = os.getenv("PGRB_BOT_GYMS_FILE")
    env["bosses_file"] = os.getenv("PGRB_BOT_BOSSES_FILE")
    env["log_level"] = os.getenv("PGRB_BOT_LOG_LEVEL")

    if os.getenv("PGRB_BOT_DEBUG_PATH") is not None:
        env["debug_folder"] = "/srv"

    # Remove None env
    env = {k: env[k] for k in env if env[k] is not None}

    # Create the bot
    bot = PoGORaidBot(**env)

    # Manage updates
    bot.listen()
