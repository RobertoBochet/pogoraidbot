from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass
from io import StringIO

from mpu.string import str2bool
from schema import Schema, Or, Optional

from data.data import Data, DataList
from data.exceptions import InvalidJSON, InvalidCSV

_logger = logging.getLogger(__name__)


@dataclass
class Boss(Data):
    level: int = None
    is_there_shiny: bool = False


class BossesList(DataList):
    @property
    def _logger(self):
        return _logger

    def _load_json(self, raw: str) -> None:
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