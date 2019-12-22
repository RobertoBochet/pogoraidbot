from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Union, List

from data.data import DataList, Data
from data.exceptions import InvalidJSON

gyms: Union[List[Gym], None] = None

_logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class Gym(Data):
    latitude: float = None
    longitude: float = None


class GymsList(DataList):
    @property
    def _logger(self):
        return _logger

    def _load_json(self, raw: str) -> None:
        try:
            data = json.loads(raw)
        except ValueError:
            raise InvalidJSON

        # Try to find a list of gyms in first level of the file
        gyms_raw = None
        for _, l in data.items():
            if isinstance(l, list):
                if isinstance(l[0], dict):
                    if "name" in l[0] and "latitude" in l[0] and "longitude" in l[0]:
                        gyms_raw = l
                        break

        # Check if a list is found
        if gyms_raw is None:
            raise InvalidJSON

        self.clear()

        # Add each gyms to the list
        for g in gyms_raw:
            self.append(Gym(g["name"], g["latitude"], g["longitude"]))
