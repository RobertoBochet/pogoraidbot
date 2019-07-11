from __future__ import annotations

import datetime
import random
import string
from dataclasses import dataclass, field
from typing import Dict


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

    def add_participant(self, id: int, name: str) -> None:
        if id in self.participants:
            self.participants[id].name = name
            self.participants[id].number += 1
            self.participants[id].is_flyer = False
        else:
            self.participants[id] = Participant(id, name)

    def add_flyer(self, id: int, name: str) -> None:
        if id in self.participants:
            self.participants[id].name = name
            self.participants[id].number += 1
            self.participants[id].is_flyer = True
        else:
            self.participants[id] = Participant(id, name, is_flyer=True)

    def remove_participant(self, id: int) -> bool:
        if id in self.participants:
            if self.participants[id].number > 1:
                self.participants[id].number -= 1
            else:
                del self.participants[id]
            return True
        return False

    def to_msg(self) -> str:

        msg = []

        if self.is_hatched:
            msg.append("<b>Boss</b>")

        msg.append("<code>{}</code>".format("\U00002B50" * self.level))
        msg.append("<i>{}</i>".format(self.gym_name))

        if self.hatching is not None:
            msg.append("<pre>Hatching:  {}{}</pre>"
                       .format("~" if self.is_aprx_time else " ", self.hatching.strftime("%H:%M")))

        if self.end is not None:
            msg.append("<pre>End:       {}{}</pre>"
                       .format("~" if self.is_aprx_time else " ", self.end.strftime("%H:%M")))

        if self.hangout is not None:
            msg.append("<pre>Hangout:    {}</pre>".format(self.hangout.strftime("%H:%M")))

        msg.append("<code>[{}]</code>".format(self.code))

        if len(self.participants) is not 0:
            msg.append("<b>--------------</b>")
            for p in self.participants:
                v = self.participants[p]
                msg.append("{}@{} {}".format(
                    "\U0001F6E9" if v.is_flyer else "",
                    v.name,
                    "" if v.number == 1 else "+{}".format(v.number - 1)))

        return "\n".join(msg)


@dataclass
class Participant:
    id: int
    name: str
    is_flyer: bool = False
    number: int = 1
