from __future__ import annotations

import datetime
import random
import string
from dataclasses import dataclass, field
from functools import reduce
from typing import Dict

from jinja2 import Template
from telegram import User

from boss import Boss
from gym import Gym


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

    @property
    def participants_count(self) -> int:
        return reduce((lambda x, y: x + y), [p.number for _, p in self.participants.items()], 0)

    def to_msg(self) -> str:
        TEMPLATE = Template(
            "{% if raid.is_ex %}"
            "*EX* "
            "{% endif %}"
            "{% if raid.gym.latitude is not none and raid.gym.longitude is not none %}"
            "[{{ raid.gym.name|wordwrap(25) }}](http://maps.google.com/maps?"
            "q={{ raid.gym.latitude }},{{ raid.gym.longitude }}"
            "&ll={{ raid.gym.latitude }},{{ raid.gym.longitude }}"
            "&z=17)\n"
            "{% else %}"
            "{{ raid.gym_name|wordwrap(25) }}\n"
            "{% endif %}"
            "\n"
            "{% if raid.is_hatched and raid.boss is not none %}"
            "*{{ raid.boss }}*\n"
            "{% endif %}"
            "{% if raid.level is not none %}"
            "{% for i in range(0, raid.level) %}\U00002B50{% endfor %}\n"
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
            "[{{ p.username }}](tg://user?id={{ id }})"
            "{% if p.is_flyer %}\U0001F6E9{% endif %}"
            "{% if p.number > 1 %} +{{ p.number - 1 }} {% endif %}"
            "\n"
            "{% endfor %}"
            "`─────────────────────`\n"
            "*{{ raid.participants_count }}* participants\n"
            "{% endif %}"
            "`[{{ raid.code }}]`"
        )

        return TEMPLATE.render(raid=self)
