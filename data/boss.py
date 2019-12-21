from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Union, List
from urllib.parse import urlparse

import requests
from schema import Schema, Or, Optional

_logger = logging.getLogger(__name__)


@dataclass
class Boss:
    name: str
    level: int = None
    is_there_shiny: bool = False


class BossesList(List):
    def __init__(self):
        super(BossesList, self).__init__()
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_from(self, file: str) -> bool:
        _logger.info("Try to load bosses list")

        try:
            # Check if the resource is remote
            if bool(urlparse(file).scheme):
                # Load the remote json
                response = requests.get(file)
                data = response.json()

            else:
                # Open the file and load it as json
                with open(file, 'r') as f:
                    data = json.load(f)

        except FileNotFoundError:
            _logger.warning("Failed to load the bosses list: file not found")
            return False
        except requests.exceptions.ConnectionError:
            _logger.warning("Failed to load the bosses list: an HTTP error occurred")
            return False
        except ValueError:
            _logger.warning("Failed to load the bosses list: failed to decode json")
            return False

        # Simple list of boss' names
        schema1 = Schema([str])

        # Dictionary of boss' names and level
        schema2 = Schema({
            str: Or(1, 2, 3, 4, 5)
        })

        # List of Boss objects
        schema3 = Schema([{
            "name": str,
            Optional("level"): int,
            Optional("is_there_shiny"): bool
        }])

        # Check if the list is valid
        if schema1.is_valid(data):
            self.clear()
            for b in data:
                self.append(Boss(b))

        elif schema2.is_valid(data):
            self.clear()
            for b in data:
                self.append(Boss(
                    name=b,
                    level=data[b]
                ))

        elif schema3.is_valid(data):
            self.clear()
            for b in data:
                self.append(Boss(**b))

        if self is None:
            _logger.warning("The file is in a wrong format")
            return False

        _logger.debug(self)

        _logger.info("Bosses list is loaded with {} bosses".format(len(self)))
        self._is_loaded = True
        return True

    def find(self, name: str, minimal_value: float = 0.4) -> Union[Boss, None]:
        if not self.is_loaded:
            return None

        current_most_similar_value = 0
        current_most_similar = None

        # Compare the boss_name with each boss in the list and find the most similar
        for b in self:
            r = SequenceMatcher(None, b.name.lower(), name.lower()).ratio()
            _logger.debug("{} - {}".format(r, b.name))
            if r > current_most_similar_value and r > minimal_value:
                current_most_similar_value = r
                current_most_similar = b

        return current_most_similar
