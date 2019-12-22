#!/usr/bin/env python3
import argparse
import logging

from bot import PoGORaidBot

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
    parser.add_argument("-d", "--debug-folder", dest="debug_folder", help="debug folder")
    parser.add_argument("-v", dest="log_level", action="count", default=0,
                        help="number of -v specifics level of verbosity")
    parser.add_argument("--info", dest="log_level", action="store_const", const=2, help="equal to -vv")
    parser.add_argument("--debug", dest="log_level", action="store_const", const=3, help="equal to -vvv")

    # Parses args
    args = vars(parser.parse_args())
    # Removes None elements
    args = {k: args[k] for k in args if args[k] is not None}

    # Parses the verbosity level
    if "log_level" in args:
        try:
            args["log_level"] = {
                0: logging.ERROR,
                1: logging.WARNING,
                2: logging.INFO,
                3: logging.DEBUG
            }[args["log_level"]]

        except KeyError:
            args["log_level"] = logging.DEBUG

    # Creates the bot
    bot = PoGORaidBot(**args)

    # Manages updates
    bot.listen()
