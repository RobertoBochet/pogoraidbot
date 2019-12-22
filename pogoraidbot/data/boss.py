from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
from io import StringIO
from typing import Union, List
from urllib.parse import urlparse

import requests
from mpu.string import str2bool
from schema import Schema, Or, Optional

from data.exceptions import InvalidJSON, InvalidCSV

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
                raw = requests.get(file).text

            else:
                # Open the file and load it as json
                with open(file, 'r') as f:
                    raw = f.read()

        except FileNotFoundError:
            _logger.warning("Failed to load the bosses list: file not found")
            return False
        except requests.exceptions.ConnectionError:
            _logger.warning("Failed to load the bosses list: an HTTP error occurred")
            return False

        try:
            self._load_json(raw)
            self._is_loaded = True
        except InvalidJSON:
            pass

        try:
            self._load_csv(raw)
            self._is_loaded = True
        except InvalidCSV:
            pass

        if not self.is_loaded:
            _logger.warning("The file is in a wrong format")
            return False

        _logger.debug(self)

        _logger.info("Bosses list is loaded with {} bosses".format(len(self)))

        return True

    def _load_json(self, raw: str) -> None:
        _logger.debug("Try JSON format")
        try:
            data = json.loads(raw)
        except ValueError:
            raise InvalidJSON

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
            return

        elif schema2.is_valid(data):
            self.clear()
            for b in data:
                self.append(Boss(
                    name=b,
                    level=data[b]
                ))
            return

        elif schema3.is_valid(data):
            self.clear()
            for b in data:
                self.append(Boss(**b))
            return

        raise InvalidJSON

    def _load_csv(self, raw: str) -> None:
        _logger.debug("Try csv format")

        rows = csv.reader(StringIO(raw))

        c = len(next(rows))

        if c == 1:
            for row in rows:
                self.append(Boss(row[0]))
            return

        elif c == 2:
            for row in rows:
                try:
                    if int(row[1]) < 0 or int(row[1]) > 5:
                        raise InvalidCSV
                except:
                    raise InvalidCSV

                self.append(Boss(row[0], int(row[1])))
            return

        elif c == 3:
            for row in rows:
                try:
                    if int(row[1]) < 0 or int(row[1]) > 5:
                        raise InvalidCSV
                    str2bool(row[2])
                except:
                    raise InvalidCSV

                self.append(Boss(row[0], int(row[1]), str2bool(row[2])))
            return

        raise InvalidCSV

    def find(self, name: str, minimal_value: float = 0.4) -> Union[Boss, None]:
        if not self.is_loaded:
            return None

        _logger.debug("Try to find a candidate for '{}'".format(name))
        # Compare the boss_name with each boss in the list and find the most similar

        values = map(lambda x: (x, SequenceMatcher(None, name.lower(), x.name.lower()).ratio()), self)

        value = max(values, key=lambda x: x[1])

        if value[1] >= minimal_value:
            _logger.debug("Found '{}' with confidence {:.3f}".format(value[0].name, value[1]))
            return value[0]
        else:
            _logger.debug("No candidate found")
            return None
