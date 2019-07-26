from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Union, List
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

gyms: Union[List[Gym], None] = None

logger = logging.getLogger(__name__)


@dataclass
class Gym:
    name: str
    latitude: float
    longitude: float


def find_gym(gym_name: str) -> Union[Gym, None]:
    # check if there is a list of gyms
    if gyms is None:
        return None

    # Minimal value required to consider similar two gyms
    minimal_value = 0.6

    current_most_similar_value = 0
    current_most_similar = None

    # Compare the gym_name with each gym in the list and find the most similar
    for g in gyms:
        r = SequenceMatcher(None, g.name, gym_name).ratio()
        if r > current_most_similar_value and r > minimal_value:
            current_most_similar_value = r
            current_most_similar = g

    return current_most_similar


def load_gyms_list(gyms_file: str) -> bool:
    global gyms
    gyms = None

    logger.info("Try to load gyms list")

    try:
        # Check if the resource is remote
        if bool(urlparse(gyms_file).scheme):
            # Load the remote json
            data = json.loads(urlopen(gyms_file).read())

        else:
            # Open the gyms file and load it as json
            with open(gyms_file, 'r') as f:
                data = json.load(f)

    except FileNotFoundError:
        logger.warning("Failed to load the gyms list: file not found")
        return False
    except HTTPError:
        logger.warning("Failed to load the gyms list: an HTTP error occurred")
        return False
    except json.decoder.JSONDecodeError:
        logger.warning("Failed to load the gyms list: failed to decode json")
        return False

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
        logger.warning("List of gyms not found in the file")
        return False

    gyms = []

    # Add each gyms to the list
    for g in gyms_raw:
        gyms.append(Gym(g["name"], g["latitude"], g["longitude"]))

    logger.info("Gyms list is loaded with {} gyms".format(len(gyms)))

    return True
