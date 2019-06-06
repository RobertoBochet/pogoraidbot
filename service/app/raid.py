import random
import string
from dataclasses import dataclass, field
from typing import List


@dataclass
class Raid:
    code: str = field(
        default_factory=lambda: "".join(random.choice(string.ascii_letters + string.digits) for i in range(8)))
    gym_name: str = None
    level: int = None
    end: any = None
    hatching: any = None
    hangout: any = None
    boss: str = None
    aprx_time: bool = False
    participants: List = field(default_factory=lambda: [])

    @property
    def is_hatched(self) -> bool:
        return self.hatching is None

    @property
    def is_egg(self) -> bool:
        return self.hatching is not None

    def to_msg(self) -> str:

        level = ("\U00002B50" * self.level).center(20 - round(1.5 * self.level))

        hatching = self.hatching.strftime("%H:%M")
        end = self.end.strftime("%H:%M")

        if self.aprx_time:
            hatching = "~" + hatching
            end = "~" + end

        msg = []

        if self.is_hatched:
            msg.append("<b>Boss</b>")

        msg.append("<code>{}</code>".format(level))
        msg.append("<i>{}</i>".format(self.gym_name))

        if self.is_egg:
            msg.append("<pre>Hatching:      {}</pre>".format(hatching))

        msg.append("<pre>End:          {}</pre>".format(end))

        if self.hangout is not None:
            msg.append("<pre>Hangout:          {}</pre>".format(self.hangout.strftime("%H:%M")))

        msg.append("<code>[{}]</code>".format(self.code))

        if len(self.participants) is not 0:
            msg.append("<b>--------------</b>")
            pass

        return "\n".join(msg)
