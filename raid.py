from __future__ import annotations

import datetime
import random
import string
from dataclasses import dataclass, field
from typing import Dict
from telegram import User
import textwrap


@dataclass
class Participant:
    id: int
    username: str
    is_flyer: bool = False
    number: int = 1


@dataclass
class Raid:
    code: str = field(
        default_factory=lambda: "".join(random.choice(string.ascii_letters + string.digits) for i in range(8)))
    gym_name: str = None
    level: int = None
    is_hatched: bool = False
    end: datetime.time = None
    hatching: datetime.time = None
    hangout: datetime.time = None
    boss: str = None
    is_aprx_time: bool = False
    participants: Dict[int, Participant] = field(default_factory=lambda: {})

    def add_participant(self, user: User) -> None:
        if user.id in self.participants:
            self.participants[user.id].username = user.username
            self.participants[user.id].number += 1
            self.participants[user.id].is_flyer = False
        else:
            self.participants[user.id] = Participant(user.id, user.username)

    def add_flyer(self, user: User) -> None:
        if user.id in self.participants:
            self.participants[user.id].username = user.username
            self.participants[user.id].number += 1
            self.participants[user.id].is_flyer = True
        else:
            self.participants[user.id] = Participant(user.id, user.username, is_flyer=True)

    def remove_participant(self, user: User) -> bool:
        if user.id in self.participants:
            if self.participants[user.id].number > 1:
                self.participants[user.id].number -= 1
            else:
                del self.participants[user.id]
            return True
        return False

    def to_msg(self) -> str:
        msg = []

        msg.append("\n".join(textwrap.wrap("_{}_".format(self.gym_name), 25)))

        msg.append("")
        if self.is_hatched:
            msg.append("*Boss*")
        if self.level is not None:
            msg.append("`{}`".format("\U00002B50" * self.level))
        msg.append("")

        if self.hatching is not None:
            msg.append("`Hatching:      {}{}`"
                       .format("~" if self.is_aprx_time else " ", self.hatching.strftime("%H:%M")))

        if self.end is not None:
            msg.append("`End:           {}{}`"
                       .format("~" if self.is_aprx_time else " ", self.end.strftime("%H:%M")))

        if self.hangout is not None:
            msg.append("`Hangout:        {}`".format(self.hangout.strftime("%H:%M")))

        if len(self.participants) is not 0:
            c = 0
            msg.append("`─────────────────────`")

            for p in self.participants:
                v = self.participants[p]
                msg.append("[{}](tg://user?id={}){} {}".format(
                    v.username, p,
                    "\U0001F6E9" if v.is_flyer else "",
                    "" if v.number == 1 else "+{}".format(v.number - 1)))
                c += v.number

            msg.append("`─────────────────────`")
            msg.append("*{}* participants".format(c))

        msg.append("`[{}]`".format(self.code))

        return "\n".join(msg)
