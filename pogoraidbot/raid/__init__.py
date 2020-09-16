from __future__ import annotations

import datetime
import random
import string
from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from typing import Dict

from telegram import User
from telegram.utils import helpers

from ..data import Boss, Gym


@dataclass
class Participant:
    class Type(Enum):
        NORMAL = 1
        REMOTE = 2
        REMOTE_INVITE = 3
        FLYER = 4

    id: int
    name: str
    type: Type = Type.NORMAL
    number: int = 1

    @property
    def is_remote(self) -> bool:
        return self.type == Participant.Type.REMOTE

    @property
    def is_remote_invite(self) -> bool:
        return self.type == Participant.Type.REMOTE_INVITE

    @property
    def is_flyer(self) -> bool:
        return self.type == Participant.Type.FLYER


@dataclass
class Raid:
    code: str = field(
        default_factory=lambda: "".join(random.choice(string.ascii_letters + string.digits) for i in range(8)))
    gym: Gym = None
    is_ex: bool = False
    level: int = None
    is_hatched: bool = False
    end: datetime.time = None
    hatching: datetime.time = None
    hangout: datetime.time = None
    boss: Boss = None
    is_aprx_time: bool = False
    participants: Dict[int, Participant] = field(default_factory=lambda: {})

    def add_participant(self, user: User) -> None:
        if user.id in self.participants:
            self.participants[user.id].name = user.full_name
            self.participants[user.id].number += 1
        else:
            self.participants[user.id] = Participant(user.id, user.full_name)

    def remove_participant(self, user: User) -> bool:
        if user.id in self.participants:
            if self.participants[user.id].number > 1:
                self.participants[user.id].name = user.full_name
                self.participants[user.id].number -= 1
            else:
                del self.participants[user.id]
            return True
        return False

    def toggle_remote(self, user: User) -> None:
        self.toggle_participant_type(user, Participant.Type.REMOTE)

    def toggle_remote_invite(self, user: User) -> None:
        self.toggle_participant_type(user, Participant.Type.REMOTE_INVITE)

    def toggle_flyer(self, user: User) -> None:
        self.toggle_participant_type(user, Participant.Type.FLYER)

    def toggle_participant_type(self, user: User, participant_type: Participant.Type) -> None:
        if user.id not in self.participants:
            self.add_participant(user)

        self.participants[user.id].name = user.full_name
        self.participants[user.id].type = participant_type \
            if self.participants[user.id].type != participant_type else Participant.Type.NORMAL

    @property
    def participants_count(self) -> int:
        return reduce((lambda x, y: x + y), [p.number for _, p in self.participants.items()], 0)

    @property
    def effective_level(self) -> int:
        if self.boss is not None:
            if self.boss.level is not None:
                return self.boss.level
        return self.level

    def to_msg(self) -> str:
        msg = ""

        if self.is_ex:
            msg += "*EX*"

        if self.gym.latitude is not None and self.gym.longitude is not None:
            msg += "[{}]({})".format(
                helpers.escape_markdown(self.gym.name, version=2),
                helpers.escape_markdown(self.gym.map, version=2))
        else:
            msg += "{}".format(helpers.escape_markdown(self.gym.name, version=2))

        msg += "\n\n"

        if self.boss is not None:
            if self.boss.is_there_shiny:
                msg += "\U00002728*{}*\U00002728".format(self.boss.name)
            else:
                msg += "{}".format(self.boss.name)
            msg += "\n"

        if self.effective_level is not None:
            msg += "\U00002B50" * self.effective_level
            msg += "\n"

        msg += "\n"

        if self.hatching is not None:
            msg += "`Hatching:   {}{}`\n".format("~" if self.is_aprx_time else " ", self.hatching.strftime('%H:%M'))

        if self.end is not None:
            msg += "`Ends:       {}{}`\n".format("~" if self.is_aprx_time else " ", self.end.strftime('%H:%M'))

        if self.hangout is not None:
            msg += "`Hangout:     {}`\n".format(self.hangout.strftime('%H:%M'))

        if self.participants_count > 0:
            msg += "`─────────────────────`\n"

            for p_id, p in self.participants.items():
                msg += helpers.mention_markdown(p_id, p.name, version=2)

                if p.is_remote:
                    msg += "\U0001F3E1"
                if p.is_remote_invite:
                    msg += "\U0001F48C"
                if p.is_flyer:
                    msg += "\U00002708"

                if p.number > 1:
                    msg += " \\+{}".format(p.number - 1)

                msg += "\n"

            msg += "`─────────────────────`\n"
            msg += "*{}* participants\n".format(self.participants_count)

        msg += "`[{}]`".format(self.code)

        return msg
