import logging

import cv2
import numpy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import Filters

from ScreenshotRaid import ScreenshotRaid


class PoGORaidBot():
    def __init__(self, token):
        self._token = token
        self._updater = Updater(self._token)

        self._updater.dispatcher.add_handler(MessageHandler(Filters.photo, self._simple_reply_handler))

    def listen(self):
        self._updater.start_polling()
        self._updater.idle()

    def _simple_reply_handler(self, bot, update):
        logging.info(
            "New image is arrived from {} by {}".format(update.effective_chat.title, update.effective_user.username))

        img = update.message.photo[-1].get_file().download_as_bytearray()

        screen = ScreenshotRaid(img)

        if not screen.is_raid():
            return

        logging.info("It's a valid screen of a raid")

        values = {
            "is_egg": screen.is_egg(),
            "timer": screen.get_timer(),
            "level": screen.get_level(),
            "gym_name": screen.get_gym_name()
        }

        keyboard = [[InlineKeyboardButton("\U0001F42F", callback_data='1'),
                     InlineKeyboardButton("\U0001F985", callback_data='2'),
                     InlineKeyboardButton("\U0001F999", callback_data='2')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("""
Is egg: {is_egg}
Gym: {gym_name}
Timer: {timer}
Level: {level}
""".format(**values), reply_markup=reply_markup)

        logging.info("A reply was sent")
