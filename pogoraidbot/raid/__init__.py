from __future__ import annotations

import datetime
import random
import string
from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from typing import Dict

from jinja2 import Template
from telegram import User

from ..data import Boss, Gym


@dataclass
class Participant:
    class Type(Enum):
        NORMAL = 1
        REMOTE = 2
        FLYER = 3

    id: int
    name: str
    type: Type = Type.NORMAL
    number: int = 1

    @property
    def is_remote(self) -> bool:
        return self.type == Participant.Type.REMOTE

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

    def toggle_remote(self, user: User) -> bool:
        if user.id in self.participants:
            self.participants[user.id].name = user.full_name
            self.participants[user.id].type = Participant.Type.REMOTE if self.participants[
                                                                             user.id].type != Participant.Type.REMOTE else Participant.Type.NORMAL
            return True
        return False

    def toggle_flyer(self, user: User) -> bool:
        if user.id in self.participants:
            self.participants[user.id].name = user.full_name
            self.participants[user.id].type = Participant.Type.FLYER if self.participants[
                                                                            user.id].type != Participant.Type.FLYER else Participant.Type.NORMAL
            return True
        return False

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
        TEMPLATE = Template(
            "{% if raid.is_ex %}*EX*{% endif %}"
            "{% if raid.gym.latitude is not none and raid.gym.longitude is not none %}"
                "[{{ raid.gym.name|wordwrap(25) }}](http://maps.google.com/maps?"
                "q={{ raid.gym.latitude }},{{ raid.gym.longitude }}"
                "&ll={{ raid.gym.latitude }},{{ raid.gym.longitude }}"
                "&z=17)\n"
            "{% else %}"
                "{{ raid.gym.name|wordwrap(25) }}\n"
            "{% endif %}"
            "\n"
            "{% if raid.boss is not none %}"
                "{% if raid.boss.is_there_shiny %}"
                    "\U00002728*{{ raid.boss.name }}*\U00002728\n"
                "{% else %}"
                    "*{{ raid.boss.name }}*\n"
                "{% endif %}"
            "{% endif %}"
            "{% if raid.effective_level is not none %}"
                "{% for i in range(0, raid.effective_level) %}\U00002B50{% endfor %}\n"
            "{% endif %}"
            "\n"
            "{% if raid.hatching is not none %}"
                "`Hatching:   {% if raid.is_aprx_time %}~{% endif %}{{ raid.hatching.strftime('%H:%M') }}`\n"
            "{% endif %}"
            "{% if raid.end is not none %}"
                "`End:        {% if raid.is_aprx_time %}~{% endif %}{{ raid.end.strftime('%H:%M') }}`\n"
            "{% endif %}"
            "{% if raid.hangout is not none %}"
                "`Hangout:    {% if raid.is_aprx_time %} {% endif %}{{ raid.hangout.strftime('%H:%M') }}`\n"
            "{% endif %}"
            "{% if raid.participants|count > 0 %}"
                "`─────────────────────`\n"
                "{% for id, p in raid.participants.items() %}"
                    "[{{ p.name }}](tg://user?id={{ id }})"
                    "{% if p.is_remote %}\U0001F3E1{% endif %}"
                    "{% if p.is_flyer %}\U00002708{% endif %}"
                    "{% if p.number > 1 %} +{{ p.number - 1 }} {% endif %}"
                    "\n"
                "{% endfor %}"
                "`─────────────────────`\n"
                "*{{ raid.participants_count }}* participants\n"
            "{% endif %}"
            "`[{{ raid.code }}]`"
        )

        return TEMPLATE.render(raid=self)
