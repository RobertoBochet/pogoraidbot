import datetime
import logging
import pickle
import re

import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Filters

from ScreenshotRaid import ScreenshotRaid


class PoGORaidBot():
    def __init__(self, token, host="127.0.0.1", port=6379):
        # Init and test redis connection
        self._raids_db = redis.Redis(host=host, port=port, db=0)
        self._participants_db = redis.Redis(host=host, port=port, db=1)
        self._raids_db.ping()

        # Init the bot
        self._updater = Updater(token)

        # Get the id of the bot
        self._id = self._updater.bot.get_me().id

        # Set the handler functions
        # Set the handler for screens
        self._updater.dispatcher.add_handler(
            MessageHandler(Filters.photo, self._screenshot_handler))
        # Set the handler to set the hangout
        self._updater.dispatcher.add_handler(
            MessageHandler(Filters.reply & Filters.regex(r"[0-2]?[0-9][:\.,][0-5]?[0-9]"), self._set_hangout_handler))
        # Set the handler for the buttons
        self._updater.dispatcher.add_handler(CallbackQueryHandler(self._buttons_handlers))

    def listen(self):
        # Begin to listen
        self._updater.start_polling()
        # Wait
        self._updater.idle()

    def _screenshot_handler(self, bot, update):
        logging.info("New image is arrived from {} by {}"
                     .format(update.effective_chat.title, update.effective_user.username))

        # Get the highest resolution image
        img = update.message.photo[-1].get_file().download_as_bytearray()

        # Load the screenshot
        screen = ScreenshotRaid(img)

        # Check if it's a screenshot of a raid
        if not screen.is_raid:
            return

        logging.info("It's a valid screen of a raid")

        # Get the raid dataclass
        raid = screen.to_raid()

        # Save the raid in the db
        self._raids_db.setex(raid.code, 60 * 60 * 6, pickle.dumps(raid))

        update.message.reply_html(raid.to_msg(), quote=True)

        logging.info("A reply was sent")

    def _set_hangout_handler(self, bot, update):
        # Check if the reply is for the bot
        if update.message.reply_to_message.from_user.id != self._id:
            return

        logging.info("A reply to bot message was come")

        try:
            # Search the code in the bot message
            code = re.search(r"\[([a-zA-Z0-9]{8})\]", update.message.reply_to_message.text).group(1)
            # Try to retrieve the raid information
            raid = pickle.loads(self._raids_db.get(code))
        except:
            logging.warning("A invalid reply was come")
            return

        # Find the new hangout
        result = re.search(r"([0-2]?[0-9])[:\.,]([0-5]?[0-9])", update.message.text)
        # Set new hangout
        raid.hangout = datetime.time(int(result.group(1)), int(result.group(2)))

        # TODO: improve this check method
        # Check if the old message was pinned
        try:
            pinned = self._updater.bot.get_chat(update.message.chat.id).pinned_message.message_id \
                     == update.message.reply_to_message.message_id
        except:
            pinned = False

        # Delete the old bot message and the reply
        self._updater.bot.delete_message(update.message.chat.id, update.message.message_id)
        self._updater.bot.delete_message(update.message.chat.id, update.message.reply_to_message.message_id)

        # Send new message
        new_msg = update.message.chat.send_message(raid.to_msg(), parse_mode=ParseMode.HTML,
                                                   reply_markup=InlineKeyboardMarkup([[
                                                       InlineKeyboardButton("\U0001F42F", callback_data='1'),
                                                       InlineKeyboardButton("\U0001F985", callback_data='2'),
                                                       InlineKeyboardButton("\U0001F999", callback_data='2')
                                                   ]]))

        # Re-pin the new message
        if pinned:
            bot.pin_chat_message(update.message.chat.id, new_msg.message_id, disable_notification=True)

    def _buttons_handlers(self, bot, update):
        pass
