import datetime
import logging
import pickle
import re

import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, MessageHandler, CallbackQueryHandler
from telegram.ext.filters import Filters

from screenshot import ScreenshotRaid


class PoGORaidBot():
    def __init__(self, token, host="127.0.0.1", port=6379):
        self.logger = logging.getLogger(__name__)

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
        self._updater.dispatcher.add_handler(CallbackQueryHandler(self._buttons_handler))
        # Set the handler for the pinned message notify
        self._updater.dispatcher.add_handler(MessageHandler(Filters.status_update.pinned_message, self._pinned_handler))
        # Set the handler for the errors
        self._updater.dispatcher.add_error_handler(self._error_handler)

        self.logger.info("Bot ready")

    def listen(self):
        # Begin to listen
        self._updater.start_polling()
        # Wait
        self._updater.idle()

    def _error_handler(self, bot, update, error):
        self.logger.warning('Update "{}" caused error "{}"'.format(update, error))

    def _pinned_handler(self, bot, update):
        # Check if the pin is caused by the bot
        if update.message.from_user.id != self._id:
            return
        # Remove the notify message
        bot.delete_message(update.message.chat.id, update.message.message_id)

    def _screenshot_handler(self, bot, update):
        self.logger.info("New image is arrived from {} by {}"
                     .format(update.effective_chat.title, update.effective_user.username))

        # Get the highest resolution image
        img = update.message.photo[-1].get_file().download_as_bytearray()

        # Load the screenshot
        screen = ScreenshotRaid(img)

        # Check if it's a screenshot of a raid
        if not screen.is_raid:
            return

        self.logger.info("It's a valid screen of a raid")

        # Get the raid dataclass
        raid = screen.to_raid()

        logging.debug(raid)

        # Save the raid in the db
        self._raids_db.setex(raid.code, 60 * 60 * 6, pickle.dumps(raid))

        update.message.reply_html(raid.to_msg(), quote=True)

        self.logger.info("A reply was sent")

    def _set_hangout_handler(self, bot, update):
        message = update.message
        # Check if the reply is for the bot
        if message.reply_to_message.from_user.id != self._id:
            return

        try:
            # Search the code in the bot message
            code = re.search(r"\[([a-zA-Z0-9]{8})\]", message.reply_to_message.text).group(1)
            # Try to retrieve the raid information
            raid = pickle.loads(self._raids_db.get(code))
        except:
            self.logger.warning("A invalid to bot message reply was come")
            return

        self.logger.info("A reply to bot message was come")

        # Find the new hangout
        result = re.search(r"([0-2]?[0-9])[:\.,]([0-5]?[0-9])", message.text)
        # Set new hangout
        raid.hangout = datetime.time(int(result.group(1)), int(result.group(2)))

        # Save the raid in the db
        self._raids_db.setex(raid.code, 60 * 60 * 6, pickle.dumps(raid))

        # Updates the message
        self._repost(raid, message)

    def _buttons_handler(self, bot, update):
        clb = update.callback_query

        try:
            # Validate the data
            result = re.match(r"([a-zA-Z0-9]{8})\:([afr])", clb.data)
            # Try to retrieve the raid information
            raid = pickle.loads(self._raids_db.get(result.group(1)))
            # Get operation
            op = result.group(2)
        except:
            self.logger.warning("A invalid callback query was come")
            return

        self.logger.info("A callback query was come")

        # Edit list of participants
        if op == "a":
            raid.add_participant(clb.from_user.id, clb.from_user.username)
        elif op == "f":
            raid.add_flyer(clb.from_user.id, clb.from_user.username)
        else:
            raid.remove_participant(clb.from_user.id)

        # Save the raid in the db
        self._raids_db.setex(raid.code, 60 * 60 * 6, pickle.dumps(raid))

        # Updates the message
        self._repost(raid, clb.message)

    def _repost(self, raid, message):
        if message.from_user.id != self._id:
            user_message = message
            message = message.reply_to_message

        # TODO: improve this check method
        # Check if the old message was pinned
        try:
            pinned = self._updater.bot.get_chat(message.chat.id).pinned_message.message_id \
                     == message.message_id
        except:
            pinned = False

        # Delete the old bot message and the reply if it exists
        self._updater.bot.delete_message(message.chat.id, message.message_id)
        try:
            self._updater.bot.delete_message(message.chat.id, user_message.message_id)
        except:
            pass

        # Send new message
        new_msg = message.chat.send_message(raid.to_msg(),
                                            parse_mode=ParseMode.HTML,
                                            reply_markup=InlineKeyboardMarkup([[
                                                InlineKeyboardButton("\U0001F42F", callback_data=raid.code + ":a"),
                                                InlineKeyboardButton("\U0001F985", callback_data=raid.code + ":f"),
                                                InlineKeyboardButton("\U0001F999", callback_data=raid.code + ":r")
                                            ]]))

        # Re-pin the new message
        if pinned:
            self._updater.bot.pin_chat_message(message.chat.id, new_msg.message_id, disable_notification=True)
