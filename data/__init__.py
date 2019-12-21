from typing import Union

from .boss import Boss, BossesList
from .gym import Gym, find_gym, load_gyms_list, gyms

bosses: Union[BossesList, None] = BossesList()
