import logging
import random
import re
import string

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import Filters

from ScreenshotRaid import ScreenshotRaid


class PoGORaidBot():
    def __init__(self, token):
        self._token = token

        # Init the bot
        self._updater = Updater(self._token)

        # Get the id of the bot
        self._id = self._updater.bot.get_me().id

        # Set the handler functions
        # Set the handler for screens
        self._updater.dispatcher.add_handler(
            MessageHandler(Filters.photo, self._screenshot_handler))
        # Set the handler to set the hangout
        self._updater.dispatcher.add_handler(
            MessageHandler(Filters.reply & Filters.regex(r"[0-2]?[0-9][:\.,][0-5]?[0-9]"), self._reply_handler))

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

        raid = screen.to_raid()

        values = {}

        values["raid_code"] = "".join(random.choice(string.ascii_letters + string.digits) for i in range(8))

        values["level"] = ("\U00002B50" * raid.level).center(20 - round(1.5 * raid.level))
        values["gym_name"] = raid.gym_name

        values["hatching"] = raid.hatching.strftime("%H:%M") if raid.hatching is not None else "§§§"
        values["end"] = raid.end.strftime("%H:%M") if raid.end is not None else "§§§"

        values["aprx"] = "~" if screen.time is None else " "

        msg = []
        if raid.is_hatched:
            msg.append("<b>Boss</b>")

        msg.append("<code>{level}</code>")
        msg.append("<i>{gym_name}</i>")

        if raid.is_egg:
            msg.append("<pre>Hatching:     {aprx}{hatching}</pre>")

        msg.append("<pre>End:          {aprx}{end}</pre>")
        msg.append("<code>[{raid_code}]</code>")

        update.message.reply_html("\n".join(msg).format(**values), quote=True)

        logging.info("A reply was sent")

    def _reply_handler(self, bot, update):
        # Check if the reply is for the bot
        if update.message.reply_to_message.from_user.id != self._id:
            return

        try:
            code = re.search(r"\[([a-zA-Z0-1]{8})\]", update.message.reply_to_message.text).group(1)
        except:
            return

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("\U0001F42F", callback_data='1'),
            InlineKeyboardButton("\U0001F985", callback_data='2'),
            InlineKeyboardButton("\U0001F999", callback_data='2')
        ]])

        update.message.reply_text("""
Raid code: {raid_code} 
Is egg: {is_egg}
Gym: {gym_name}
Timer: {timer}
Level: {level}
        """, reply_markup=reply_markup)
