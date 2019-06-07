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
    end: any = None
    hatching: any = None
    hangout: any = None
    boss: str = None
    is_aprx_time: bool = False
    participants: Dict = field(default_factory=lambda: {})

    def add_participant(self, id: int, name: str) -> None:
        if id in self.participants:
            v = self.participants[id]
            self.participants[id] = (name, "l", v[2] + 1)
        else:
            self.participants[id] = (name, "l", 1)

    def add_flyer(self, id: int, name: str) -> None:
        if id in self.participants:
            v = self.participants[id]
            self.participants[id] = (name, "f", v[2] + 1)
        else:
            self.participants[id] = (name, "f", 1)

    def remove_participant(self, id: int) -> bool:
        if id in self.participants:
            v = self.participants[id]
            if v[2] > 1:
                self.participants[id] = (v[0], v[1], v[2] - 1)
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
                i = "" if v[1] == "l" else "\U0001F6E9"
                n = "" if v[2] == 1 else "+{}".format(v[2])
                msg.append("{}@{} {}".format(i, v[0], n))

        return "\n".join(msg)
