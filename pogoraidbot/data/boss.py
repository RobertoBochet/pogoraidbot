from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from io import StringIO

from mpu.string import str2bool
from schema import Schema, Or, Optional

from .data import Data, DataList
from .exceptions import InvalidJSON, InvalidCSV


@dataclass
class Boss(Data):
    level: int = None
    is_there_shiny: bool = False


class BossesList(DataList):
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

        rows = csv.reader(StringIO(raw), skipinitialspace=True)

        # skips the header row and counts the columns
        c = len(next(rows))

        if c == 1:
            for row in rows:
                self.append(Boss(row[0].strip()))
            return

        elif c == 2:
            for row in rows:
                try:
                    if int(row[1].strip()) < 0 or int(row[1].strip()) > 5:
                        raise InvalidCSV
                except:
                    raise InvalidCSV

                self.append(Boss(row[0].strip(), int(row[1].strip())))
            return

        elif c == 3:
            for row in rows:
                try:
                    if int(row[1].strip()) < 0 or int(row[1].strip()) > 5:
                        raise InvalidCSV
                    str2bool(row[2].strip())
                except:
                    raise InvalidCSV

                self.append(Boss(row[0].strip(), int(row[1].strip()), str2bool(row[2].strip())))
            return

        raise InvalidCSV
