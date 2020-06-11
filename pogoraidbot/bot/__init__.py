from __future__ import annotations

import datetime
import functools
import logging
import os
import pickle
import re
import sys
import traceback
from typing import Callable

import cv2
from apscheduler.schedulers.background import BackgroundScheduler
from redis import StrictRedis, exceptions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Bot, Message, error
from telegram.ext import Updater, MessageHandler, CallbackQueryHandler, CommandHandler, CallbackContext
from telegram.ext.filters import Filters

from .. import redis_keys
from ..data import bosses, gyms
from ..raid import Raid
from ..screenshot import ScreenshotRaid

_LOGGER = logging.getLogger(__package__)

class PoGORaidBot:
    class Decorator:
        class ChatMustBeEnabled:
            def __init__(self, func: Callable[[PoGORaidBot, Update, CallbackContext], bool]):
                self.func = func

            def __get__(self, obj, objtype):
                """Support instance methods."""
                return functools.partial(self.__call__, obj)

            def __call__(self, inst: PoGORaidBot, update: Update, context: CallbackContext) -> bool:
                try:
                    chat_id = update.message.chat_id
                except AttributeError:
                    chat_id = update.callback_query.message.chat_id

                # Check if this chat is enabled
                if not inst._redis.sismember(redis_keys.ENABLEDCHAT, chat_id):
                    _LOGGER.info("Chat {} is not enabled".format(chat_id))

                    return False

                return self.func(inst, update, context)

        class UserMustBeAdmin:
            def __init__(self, func: Callable[[PoGORaidBot, Update, CallbackContext], bool]):
                self.func = func

            def __get__(self, obj, objtype):
                """Support instance methods."""
                return functools.partial(self.__call__, obj)

            def __call__(self, inst: PoGORaidBot, update: Update, context: CallbackContext) -> bool:
                is_admin = False
                # If the chat is private doesn't check administrators
                if update.message.chat.type == update.message.chat.PRIVATE:
                    is_admin = True
                else:
                    # Get the list of administrators of a chat
                    for a in context.bot.get_chat_administrators(update.message.chat.id):
                        # Check if the current admin in the user
                        if a.user.id == update.message.from_user.id:
                            is_admin = True
                            break

                # Check if the sender is an admin
                if not is_admin:
                    _LOGGER.info("User {} is not admin".format(update.message.from_user.id))

                    return False

                return self.func(inst, update, context)

        class UserMustBeBotAdmin:
            def __init__(self, func: Callable[[PoGORaidBot, Update, CallbackContext], bool]):
                self.func = func

            def __get__(self, obj, objtype):
                """Support instance methods."""
                return functools.partial(self.__call__, obj)

            def __call__(self, inst: PoGORaidBot, update: Update, context: CallbackContext) -> bool:
                # Check if the user is a bot admin
                if not inst._redis.sismember(redis_keys.ADMIN, update.message.from_user.id):
                    _LOGGER.warning("User {} is not a bot admin".format(update.message.from_user.id))

                    return False

                return self.func(inst, update, context)

    def __init__(self,
                 token: str,
                 redis: str = "redis://127.0.0.1:6379/0",
                 superadmin: int = None,
                 bosses_file: str = None,
                 bosses_expiration: int = 12,
                 gyms_file: str = None,
                 gyms_expiration: int = 12,
                 debug_folder: str = None
                 ):
        # Init and test redis connection
        self._redis = StrictRedis.from_url(url=redis, charset="utf-8", decode_responses=False)

        _LOGGER.info("Try to connect to Redis...")
        try:
            self._redis.ping()
        except exceptions.ConnectionError:
            _LOGGER.critical("Unable to connect to Redis")
            sys.exit()
        _LOGGER.info("Successfully connected to Redis")

        # Save superadmin
        self._superadmin = int(superadmin) if superadmin is not None else None
        # Add superadmin to the admins db
        if self._superadmin is not None:
            self._redis.set(redis_keys.SUPERADMIN, self._superadmin)
            self._redis.sadd(redis_keys.ADMIN, self._superadmin)

        # Save debug folder
        self._debug_folder = debug_folder
        if self._debug_folder is not None:
            self._debug_folder = os.path.abspath(debug_folder)
            ScreenshotRaid.debug = True
            _LOGGER.info("\"{}\" was set as debug folder".format(self._debug_folder))

        # Init the bot
        self._bot = Bot(token)

        # Init updater
        self._updater = Updater(bot=self._bot, use_context=True)

        # Get the id of the bot
        self._id = self._bot.get_me().id

        # Set the handler functions
        # Set the handler for screens
        self._updater.dispatcher.add_handler(MessageHandler(Filters.photo, self._handler_screenshot))
        # Set the handler to set the hangout
        self._updater.dispatcher.add_handler(MessageHandler(
            Filters.reply & Filters.regex(r"^\s*[0-2]?[0-9][:.,][0-5]?[0-9]\s*$"), self._handler_set_hangout))
        # Set the handler for the buttons
        self._updater.dispatcher.add_handler(CallbackQueryHandler(self._handler_buttons))
        # Set the handler for the pinned message notify
        self._updater.dispatcher.add_handler(MessageHandler(Filters.status_update.pinned_message,
                                                            self._handler_event_pinned))
        # Set the handler to set the boss
        self._updater.dispatcher.add_handler(MessageHandler(
            Filters.reply & Filters.regex(r"^\s*[a-zA-Z]+\s*$"), self._handler_set_boss))

        # Set the handler for scan command
        self._updater.dispatcher.add_handler(CommandHandler("scan", self._handler_command_scan))
        # Set the handler for enablechat command
        self._updater.dispatcher.add_handler(CommandHandler("enablechat", self._handler_command_enablechat))
        # Set the handler for disablechat command
        self._updater.dispatcher.add_handler(CommandHandler("disablechat", self._handler_command_disablechat))
        # Set the handler for enablescan command
        self._updater.dispatcher.add_handler(CommandHandler("enablescan", self._handler_command_enablescan))
        # Set the handler for disablescan command
        self._updater.dispatcher.add_handler(CommandHandler("disablescan", self._handler_command_disablescan))
        # Set the handler for addadmin command
        self._updater.dispatcher.add_handler(CommandHandler("addadmin", self._handler_command_addadmin, Filters.reply))
        # Set the handler for removeadmin command
        self._updater.dispatcher.add_handler(CommandHandler("removeadmin", self._handler_command_removeadmin,
                                                            Filters.reply))

        # Set the handler for the errors
        self._updater.dispatcher.add_error_handler(self._handler_error)

        # Creates background scheduler for update the db
        self._scheduler = BackgroundScheduler(daemon=True)

        # Creates job to update bosses list
        if bosses_file is not None:
            bosses.load_from(bosses_file)
            self._scheduler.add_job(lambda: bosses.load_from(bosses_file), 'interval', hours=int(bosses_expiration))

        # Creates job to update gyms list
        if gyms_file is not None:
            gyms.load_from(gyms_file)
            self._scheduler.add_job(lambda: gyms.load_from(gyms_file), 'interval', hours=int(gyms_expiration))

        # Starts the scheduler
        self._scheduler.start()

        _LOGGER.info("Bot ready")

    def listen(self) -> None:
        _LOGGER.info("Start listening")

        # Begin to listen
        self._updater.start_polling()
        # Wait
        self._updater.idle()

    def _handler_error(self, update: Update, context: CallbackContext) -> None:
        _LOGGER.warning('Update "{}" caused error "{}"'.format(update, context.error))

    @Decorator.ChatMustBeEnabled
    def _handler_event_pinned(self, update: Update, _: CallbackContext) -> bool:
        # Check if the pin is caused by the bot
        if update.message.from_user.id != self._id:
            return False

        # Remove the notify message
        self._bot.delete_message(update.message.chat.id, update.message.message_id)

        return True

    @Decorator.ChatMustBeEnabled
    def _handler_screenshot(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("New image is arrived from {} by {}"
                          .format(update.effective_chat.title, update.effective_user.username))

        # Check if scan is disabled for this group
        if self._redis.exists(update.effective_chat.id):
            _LOGGER.info("Screenshots scan for chat {} is disabled".format(update.effective_chat.id))
            return False

        # Scan the screenshot
        self._scan_screenshot(update.message)
        return True

    @Decorator.ChatMustBeEnabled
    def _handler_set_hangout(self, update: Update, _: CallbackContext) -> bool:
        # Check if the reply is for the bot
        if update.message.reply_to_message.from_user.id != self._id:
            return False

        try:
            # Search the code in the bot message
            code = re.search(r"\[([a-zA-Z0-9]{8})\]", update.message.reply_to_message.text).group(1)
            # Try to retrieve the raid information
            raid = pickle.loads(self._redis.get(redis_keys.RAID.format(code)))
        except Exception:  # TODO: improve except
            traceback.print_exc()
            _LOGGER.warning("A invalid to bot message reply was come")
            return False

        _LOGGER.info("A reply to bot message was come")

        # Find the new hangout
        result = re.search(r"([0-2]?[0-9])[:.,]([0-5]?[0-9])", update.message.text)
        # Set new hangout
        raid.hangout = datetime.time(int(result.group(1)), int(result.group(2)))

        _LOGGER.debug(raid)

        # Save the raid in the db
        self._redis.setex(redis_keys.RAID.format(raid.code), 60 * 60 * 6, pickle.dumps(raid))

        # Try to delete user message
        self._try_to_delete(update.message)

        # Updates the message
        self._post_raid(raid, update.message.reply_to_message)

        return True

    @Decorator.ChatMustBeEnabled
    def _handler_buttons(self, update: Update, _: CallbackContext) -> bool:
        try:
            # Validate the data
            result = re.match(r"([a-zA-Z0-9]{8}):([arhf])", update.callback_query.data)
            # Try to retrieve the raid information
            raid = pickle.loads(self._redis.get(redis_keys.RAID.format(result.group(1))))
            # Get operation
            op = result.group(2)
        except Exception:  # TODO: improve except
            _LOGGER.warning("A invalid callback query was come")
            return False

        _LOGGER.info("A callback query was come")

        # Edit list of participants
        if op == "a":
            raid.add_participant(update.callback_query.from_user)
        elif op == "r":
            raid.remove_participant(update.callback_query.from_user)
        elif op == "h":
            raid.toggle_remote(update.callback_query.from_user)
        elif op == "f":
            raid.toggle_flyer(update.callback_query.from_user)
        else:
            return False

        _LOGGER.debug(raid)

        # Save the raid in the db
        self._redis.setex(redis_keys.RAID.format(raid.code), 60 * 60 * 6, pickle.dumps(raid))

        # Updates the message
        self._post_raid(raid, update.callback_query.message)

        return True

    @Decorator.ChatMustBeEnabled
    def _handler_set_boss(self, update: Update, _: CallbackContext) -> bool:
        # Check if the reply is for the bot
        if update.message.reply_to_message.from_user.id != self._id:
            return False

        try:
            # Search the code in the bot message
            code = re.search(r"\[([a-zA-Z0-9]{8})\]", update.message.reply_to_message.text).group(1)
            # Try to retrieve the raid information
            raid = pickle.loads(self._redis.get(redis_keys.RAID.format(code)))
        except Exception:  # TODO: improve except
            _LOGGER.warning("A invalid to bot message reply was come")
            return False

        _LOGGER.info("A request to change boss was come from {}({}) by {}({})"
                          .format(update.effective_chat.title, update.effective_chat.id,
                                  update.effective_user.username, update.effective_user.id))

        _LOGGER.info("The user suggested \"{}\"".format(update.message.text.strip()))

        # Get the suggested boss name
        name = update.message.text.strip()

        # Search the boss
        b = bosses.find(name, 0.8)

        # If the boss wasn't found reply with an error
        if b is None:
            update.message.reply_markdown("Sorry, but i don't know *{}*".format(name))
            _LOGGER.info("A valid boss wasn't found")
            return False

        _LOGGER.info("\"{}\" was found".format(b.name))

        # Set the new boss
        raid.boss = b

        # Save the raid in the db
        self._redis.setex(redis_keys.RAID.format(raid.code), 60 * 60 * 6, pickle.dumps(raid))

        _LOGGER.debug(raid)

        # Try to delete user message
        self._try_to_delete(update.message)

        # Updates the message
        self._post_raid(raid, update.message.reply_to_message)

        return True

    @Decorator.ChatMustBeEnabled
    @Decorator.UserMustBeAdmin
    def _handler_command_disablescan(self, update: Update, _: CallbackContext) -> bool:
        # Add current chat to the db of disabled scan
        self._redis.sadd(redis_keys.DISABLEDSCAN, update.message.chat.id)

        _LOGGER.info("Disable scan for chat {}".format(update.message.chat.id))
        update.message.chat.send_message("The scan now is disabled")

        return True

    @Decorator.ChatMustBeEnabled
    @Decorator.UserMustBeAdmin
    def _handler_command_enablescan(self, update: Update, _: CallbackContext) -> bool:
        # Remove current chat from the db of disabled scan
        self._redis.srem(redis_keys.DISABLEDSCAN, update.message.chat.id)

        _LOGGER.info("Enable scan for chat {}".format(update.message.chat.id))
        update.message.chat.send_message("The scan now is enabled")

        return True

    @Decorator.ChatMustBeEnabled
    def _handler_command_scan(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("Required scan from {} by {}".format(update.message.chat.id, update.message.from_user.id))

        # Check if it is a reply to screenshot
        if update.message.reply_to_message is None or len(update.message.reply_to_message.photo) == 0:
            update.message.reply_text("It must be a reply to a screenshot")
            _LOGGER.info("Invalid scan command")
            return False

        # Try to delete user command
        self._try_to_delete(update.message)

        try:
            # Scan the screenshot
            self._scan_screenshot(update.message.reply_to_message)
        except:
            traceback.print_exc()
            return False

        return True

    @Decorator.UserMustBeBotAdmin
    def _handler_command_addadmin(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("User {} try to add {} as bot admin".format(update.message.from_user.id,
                                                                      update.message.reply_to_message.from_user.id))

        # Check if the cited user is already a bot admin
        if self._redis.sismember(redis_keys.ADMIN, update.message.reply_to_message.from_user.id):
            _LOGGER.info("User {} is already a bot admin".format(update.message.reply_to_message.from_user.id))
            update.message.reply_markdown("[{}](tg://user?id={}) is already a bot admin"
                                          .format(update.message.reply_to_message.from_user.username,
                                                  update.message.reply_to_message.from_user.id))
            return False

        # Add cited user as bot admin
        self._redis.sadd(redis_keys.ADMIN, update.message.reply_to_message.from_user.id)
        _LOGGER.info("User {} is now a bot admin".format(update.message.reply_to_message.from_user.id))
        update.message.reply_markdown("[{}](tg://user?id={}) is now a bot admin"
                                      .format(update.message.reply_to_message.from_user.username,
                                              update.message.reply_to_message.from_user.id))

        return True

    @Decorator.UserMustBeBotAdmin
    def _handler_command_removeadmin(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("User {} try to remove {} as bot admin".format(update.message.from_user.id,
                                                                         update.message.reply_to_message.from_user.id))

        # Check if the mentioned user is the superadmin
        if self._redis.get(redis_keys.SUPERADMIN) == update.message.reply_to_message.from_user.id:
            _LOGGER.info("User {} is the superadmin".format(update.message.reply_to_message.from_user.id))
            update.message.reply_markdown("[{}](tg://user?id={}) is the superadmin and it cannot be removed"
                                          .format(update.message.reply_to_message.from_user.username,
                                                  update.message.reply_to_message.from_user.id))
            return False

        # Check if the cited user is not a bot admin
        if not self._redis.sismember(redis_keys.ADMIN, update.message.reply_to_message.from_user.id):
            _LOGGER.info("User {} is not a bot admin".format(update.message.reply_to_message.from_user.id))
            update.message.reply_markdown("[{}](tg://user?id={}) is not a bot admin"
                                          .format(update.message.reply_to_message.from_user.username,
                                                  update.message.reply_to_message.from_user.id))
            return False

        # Remove cited user as bot admin
        self._redis.srem(redis_keys.ADMIN, update.message.reply_to_message.from_user.id)
        _LOGGER.info("User {} is no longer a bot admin".format(update.message.reply_to_message.from_user.id))
        update.message.reply_markdown("[{}](tg://user?id={}) is no longer a bot admin"
                                      .format(update.message.reply_to_message.from_user.username,
                                              update.message.reply_to_message.from_user.id))

        return True

    @Decorator.UserMustBeBotAdmin
    def _handler_command_enablechat(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("Bot admin {} try to enable the chat {}".format(update.message.from_user.id,
                                                                          update.message.chat.id))

        # Check if this chat is already enabled
        if self._redis.sismember(redis_keys.ENABLEDCHAT, update.message.chat.id):
            _LOGGER.info("Chat {} is already enabled".format(update.message.chat.id))
            update.message.reply_markdown("This chat is already enabled")
            return False

        # Add this chat to the enabled
        self._redis.sadd(redis_keys.ENABLEDCHAT, update.message.chat.id)
        _LOGGER.info("Chat {} is now enabled".format(update.message.chat.id))
        update.message.reply_markdown("This chat is now enabled")

        return True

    @Decorator.UserMustBeBotAdmin
    def _handler_command_disablechat(self, update: Update, _: CallbackContext) -> bool:
        _LOGGER.info("Bot admin {} try to disable the chat {}".format(update.message.from_user.id,
                                                                           update.message.chat.id))

        # Check if this chat is not enabled
        if not self._redis.sismember(redis_keys.ENABLEDCHAT, update.message.chat.id):
            _LOGGER.info("Chat {} is not enabled".format(update.message.chat.id))
            update.message.reply_markdown("This chat is not enabled")
            return False

        # Remove this chat to the enabled
        self._redis.srem(redis_keys.ENABLEDCHAT, update.message.chat.id)
        _LOGGER.info("Chat {} is no longer enabled".format(update.message.chat.id))
        update.message.reply_markdown("This chat is no longer enabled")

        return True

    def _scan_screenshot(self, message: Message) -> None:
        # Get the highest resolution image
        img = message.photo[-1].get_file().download_as_bytearray()

        # Load the screenshot
        screen = ScreenshotRaid(img)

        # Check if it's a screenshot of a raid
        if not screen.is_raid:
            return

        _LOGGER.info("It's a valid screen of a raid")

        # Get the raid dataclass
        raid = screen.to_raid()

        # Save the raid in the db
        self._redis.setex(redis_keys.RAID.format(raid.code), 60 * 60 * 6, pickle.dumps(raid))

        # Send reply
        try:
            self._post_raid(raid, message)
        except:
            traceback.print_exc()  # TODO: Remove this debug method

        # Save sections of image if it is required
        if self._debug_folder is not None:
            try:
                os.makedirs(self._debug_folder, exist_ok=True)

                res = cv2.imwrite(os.path.join(self._debug_folder, "{}-anchors.png".format(raid.code)),
                                  screen._get_anchors_image())
                for s in screen._image_sections:
                    res = cv2.imwrite(os.path.join(self._debug_folder, "{}-{}.png".format(raid.code, s)),
                                      screen._image_sections[s]) and res
                if not res:
                    _LOGGER.warning("Something was gone wrong during save sections of image")

            except PermissionError:
                _LOGGER.warning("Unable to create debug folder")

    def _post_raid(self, raid: Raid, message: Message) -> None:
        options = {
            "disable_web_page_preview": True,
            "parse_mode": ParseMode.MARKDOWN
        }

        # If the hangout is defined add the reply button to the message
        if raid.hangout is not None:
            options["reply_markup"] = InlineKeyboardMarkup([[
                InlineKeyboardButton("\U00002795", callback_data=raid.code + ":a"),
                InlineKeyboardButton("\U00002796", callback_data=raid.code + ":r"),
                InlineKeyboardButton("\U0001F3E1", callback_data=raid.code + ":h"),
                InlineKeyboardButton("\U00002708", callback_data=raid.code + ":f")
            ]])

        # If the reference message is a screenshot, the bot replies to that
        elif message.from_user.id != self._id:
            options["reply_to_message_id"] = message.message_id

        # TODO: improve this check method
        # Check if the old message was pinned
        try:
            pinned = self._bot.get_chat(message.chat.id).pinned_message.message_id == message.message_id
        except AttributeError:
            pinned = False

        # Try to delete the screenshot if it's necessary
        if message.reply_to_message is not None and raid.hangout is not None:
            self._try_to_delete(message.reply_to_message)

        # Try to delete the old message
        if message.from_user.id == self._id:
            self._try_to_delete(message)

        # Send new message
        new_msg = message.chat.send_message(raid.to_msg(),
                                            **options)

        # Re-pin the new message
        if pinned:
            self._bot.pin_chat_message(message.chat.id, new_msg.message_id, disable_notification=True)

    def _try_to_delete(self, message: Message):
        try:
            self._bot.delete_message(message.chat.id, message.message_id)
        except error.BadRequest:
            _LOGGER.info("The bot hasn't the permission to delete messages")

    def _init_db(self):
        pass
