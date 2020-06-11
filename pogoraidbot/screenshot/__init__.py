import datetime
import logging
import re
from difflib import SequenceMatcher
from functools import reduce
from typing import Tuple, Union

import cv2
import numpy as np
import pytesseract

from . import resources
from ..cachedmethod import CachedMethod
from ..data import Boss, Gym, gyms, bosses
from ..exceptions import HatchingTimerNotFound, HatchingTimerUnreadable, RaidTimerNotFound, RaidTimerUnreadable, \
    ExTagNotFound, ExTagUnreadable, LevelNotFound, TimeNotFound, HatchingTimerException, RaidTimerException, \
    GymNotFound, ExTagException, BossNotFound, BossesListNotAvailable
from ..raid import Raid

Rect = Tuple[Tuple[int, int], Tuple[int, int]]

_LOGGER = logging.getLogger(__package__)


class ScreenshotRaid:
    debug = False

    def __init__(self, img: Union[np.ndarray, bytearray]):

        if isinstance(img, np.ndarray):
            self._img = img
        elif isinstance(img, bytearray):
            self._img = cv2.imdecode(np.asarray(img, dtype="uint8"), cv2.IMREAD_COLOR)
        else:
            raise Exception  # TODO: create adhoc exception

        if ScreenshotRaid.debug:
            self._image_sections = {}

        self._size = (len(self._img[0]), len(self._img))

        self._anchors = {}
        self._anchors_available = 0

        self._find_anchors()

    def _calc_subset(self, *subs) -> Rect:
        if len(subs) == 1 and isinstance(subs[0], tuple):
            subs = subs[0]
        elif len(subs) == 2:
            subs = list(subs)
        else:
            raise Exception

        points = [[None, None], [None, None]]

        for i in [0, 1]:
            # Amount of pixels centered
            if isinstance(subs[i], int):
                points[0][i] = round(self._size[i] / 2 - subs[i] / 2 - 1)
                points[1][i] = round(self._size[i] / 2 + subs[i] / 2 - 1)

            # Perceptual of pixels centered
            elif isinstance(subs[i], float):
                points[0][i] = round((self._size[i] - 1) / 2 - subs[i] * (self._size[i] - 1) / 2)
                points[1][i] = round((self._size[i] - 1) / 2 + subs[i] * (self._size[i] - 1) / 2)

            else:
                for j in [0, 1]:
                    v = subs[i][j]
                    if isinstance(v, float):
                        if v < 0:
                            points[j][i] = round((self._size[i] - 1) * v) + self._size[i]
                        else:
                            points[j][i] = round((self._size[i] - 1) * v)
                    else:
                        if v < 0:
                            points[j][i] = v + self._size[i]
                        else:
                            points[j][i] = v

        return (tuple(points[0]), tuple(points[1]))

    def _subset(self, rect: Rect) -> np.ndarray:
        return self._img[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]

    def _read_hatching_timer(self) -> datetime.timedelta:
        if self.hatching_timer_position is None:
            raise HatchingTimerNotFound
        img = self._subset(self.hatching_timer_position)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY_INV)

        if ScreenshotRaid.debug:
            self._image_sections["hatching_timer"] = img

        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        _LOGGER.debug("raw hatching_timer «{}»".format(text))

        result = re.search(r"([0-3])[:.]([0-5][0-9])[:.]([0-5][0-9])", text)

        try:
            _LOGGER.debug("hatching_timer {}:{}:{}".format(result.group(1), result.group(2), result.group(3)))
            return datetime.timedelta(hours=int(result.group(1)), minutes=int(result.group(2)),
                                      seconds=int(result.group(3)))
        except Exception:
            pass

        _LOGGER.debug("hatching timer unreadable")
        raise HatchingTimerUnreadable

    def _find_hatching_timer(self) -> Rect:
        red_lower = np.array([150, 100, 230])
        red_upper = np.array([255, 130, 255])

        sub = self._calc_subset(0.35, (0.15, 0.29))

        img = self._subset(sub)
        img = cv2.GaussianBlur(img, (5, 5), 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(img, red_lower, red_upper)

        if ScreenshotRaid.debug:
            self._image_sections["hatching_timer_mask"] = mask

        try:
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            x, y, w, h = cv2.boundingRect(
                reduce((lambda x, y: x if cv2.contourArea(x) > cv2.contourArea(y) else y), contours))

            return ((sub[0][0] + x, sub[0][1] + y), (sub[0][0] + x + w, sub[0][1] + y + h))
        except:
            pass

        _LOGGER.debug("hatching timer not found")
        raise HatchingTimerNotFound

    def _read_raid_timer(self) -> datetime.timedelta:
        if self.raid_timer_position is None:
            raise RaidTimerNotFound
        img = self._subset(self.raid_timer_position)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY_INV)

        if ScreenshotRaid.debug:
            self._image_sections["raid_timer"] = img

        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        _LOGGER.debug("raw raid_timer «{}»".format(text))

        result = re.search(r"([0-3])[:.]([0-5][0-9])[:.]([0-5][0-9])", text)

        try:
            _LOGGER.debug("raid_timer {}:{}:{}".format(result.group(1), result.group(2), result.group(3)))
            return datetime.timedelta(hours=int(result.group(1)), minutes=int(result.group(2)),
                                      seconds=int(result.group(3)))
        except Exception:
            pass

        _LOGGER.debug("raid timer unreadable")
        raise RaidTimerUnreadable

    def _find_raid_timer(self) -> Rect:
        red_lower = np.array([-50, 175, 230])
        red_upper = np.array([50, 205, 255])

        sub = self._calc_subset(((-0.30, -0.02), (0.54, 0.65)))

        img = self._subset(sub)
        img = cv2.GaussianBlur(img, (5, 5), 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(img, red_lower, red_upper)

        if ScreenshotRaid.debug:
            self._image_sections["raid_timer_mask"] = mask

        try:
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            x, y, w, h = cv2.boundingRect(
                reduce((lambda x, y: x if cv2.contourArea(x) > cv2.contourArea(y) else y), contours))

            return ((sub[0][0] + x, sub[0][1] + y), (sub[0][0] + x + w, sub[0][1] + y + h))
        except:
            pass

        _LOGGER.debug("raid timer not found")
        raise RaidTimerNotFound

    def _find_gym(self) -> Gym:
        # TODO: improve find gym method
        try:
            x, y, r = self._anchors["gym_image"]

            sub = self._calc_subset((x + r + 10, -160), (y - r + 5, y + r - 5))
        except:
            sub = self._calc_subset((200, -160), (60, 150))

        img = self._subset(sub)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY_INV)
        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        _LOGGER.debug("raw gym_name «{}»".format(text))

        text = text.rstrip().replace('\n', ' ')
        text = " ".join(text.split())

        logging.debug(text)

        if ScreenshotRaid.debug:
            self._image_sections["gym_name"] = img

        g = gyms.find(text)

        if g is not None:
            return g

        return Gym(name=text)
        # TODO: add the exception case

    def _find_boss(self) -> Union[Boss, None]:
        # Check if a list of available bosses was provided
        if not bosses.is_loaded:
            raise BossesListNotAvailable

        # Force the calc of the level if it isn't already calculated
        _ = self.level

        # Calculate the subset based on the level position
        try:
            (_, _), (_, y) = self._anchors["level"]
            sub = self._calc_subset(0.8, (y + 85, y + 215))
        except:
            sub = self._calc_subset(0.8, (0.23, 0.34))

        # Create the subset of the screenshot and filter it
        img = self._subset(sub)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)

        if ScreenshotRaid.debug:
            self._image_sections["boss"] = img

        # Find the text in the subset
        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        _LOGGER.debug("raw boss «{}»".format(text))

        # Removed new line from the text
        text = text.rstrip().replace('\n', ' ')
        text = " ".join(text.split())

        # Try to find a boss from text
        b = bosses.find(text)

        # Check if a valid boss was found
        if b is None:
            raise BossNotFound

        return b

    def _find_ex_tag(self) -> Rect:
        # Prepare a range of colors to search the ex label in HSV color space
        color = np.array([133, 138, 189])
        color_offset = np.array([50, 15, 13])
        color_range = color - color_offset, color + color_offset

        # Calculate a subset of coordinates in the screenshot where the ex label could be
        sub = self._calc_subset((-230, 1.0), (30, 100))

        # Create the subset of the screenshot, filter it and move it in the HSV color space
        img = self._subset(sub)
        img = cv2.GaussianBlur(img, (5, 5), 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Create a mask of the image in the range of colors and dilate it with the aim of reduce the noise
        mask = cv2.inRange(img, *color_range)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))

        if ScreenshotRaid.debug:
            self._image_sections["ex_tag_mask"] = mask

        # Try to search contours of mask
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            # Search the biggest blob and calculate the bounding rectangle
            x, y, w, h = cv2.boundingRect(
                reduce((lambda x, y: x if cv2.contourArea(x) > cv2.contourArea(y) else y), contours))

            # Return the position of the bounding rectangle of the biggest blob
            return ((sub[0][0] + x, sub[0][1] + y), (sub[0][0] + x + w, sub[0][1] + y + h))

        # It wasn't found a candidate as ex label
        raise ExTagNotFound

    def _check_ex_tag(self) -> bool:
        # Check if it was found a candidate as ex label
        if self.ex_tag_position is None:
            raise ExTagNotFound

        # Get a sub image of the possible ex label and binarize it
        img = self._subset(self.ex_tag_position)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY_INV)

        if ScreenshotRaid.debug:
            self._image_sections["ex_tag"] = img

        # Read the sub image
        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        _LOGGER.debug("raw ex_tag «{}»".format(text))

        # If it is enough similar to ex label the gym will be considered ex
        if max([SequenceMatcher(None, "ex raid", text.lower()).ratio(),
                SequenceMatcher(None, "raid ex", text.lower()).ratio()]) > 0.4:
            return True

        raise ExTagUnreadable

    def _find_level(self) -> int:
        # For eggs and hatched different parameters are used
        if self.is_egg:
            ht_pos = self.hatching_timer_position
            sub = self._calc_subset(0.55, (ht_pos[1][1] + 15, ht_pos[1][1] + 105))
            template = resources.LEVEL_EGG
            mask = resources.LEVEL_MASK_EGG
            threshold = 0.914
            matchf = lambda img: cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED, None, mask)
        else:
            sub = self._calc_subset(0.5, (0.10, 0.20))
            template = resources.LEVEL_HATCHED
            mask = resources.LEVEL_MASK_HATCHED
            threshold = 0.94
            matchf = lambda img: cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED, None, mask)

        # Get the subset image
        img = self._subset(sub)

        # Search match of the marker in the gray scale subset
        res = matchf(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

        # Filter the results with a threshold
        loc = np.where(res >= threshold)

        # The point found must be merged
        # Number of recurrences of unique points
        occ = []
        # Contains unique points
        matches = []
        # Parse all the points found
        for a in np.dstack(loc[::-1])[0]:
            # Compare all the point with other unique points evaluate the distance
            for i, match in enumerate(matches):
                # If the point is almost near to the unique point merges that
                if np.linalg.norm(a - match) <= 10:
                    matches[i] = (match * occ[i] + a) // (occ[i] + 1)
                    occ[i] += 1
                    a = None
                    break
            # if the point is not almost near to another unique point mark it as unique point
            if a is not None:
                matches.append(a)
                occ.append(1)

        # Calculate the mean of vertical position of the points
        mean = np.mean([i[1] for i in matches]) if len(matches) > 0 else 0
        # Remove all the points that that are too far between themselves
        marker = list(filter(lambda x: abs(x[1] - mean) < 20, matches))

        w, h = template.shape[::-1]

        if ScreenshotRaid.debug:
            for pt in marker:
                cv2.rectangle(img, (pt[0], pt[1]), (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            self._image_sections["level"] = img

        # Count the matches to calculate the level
        level = len(matches) if len(matches) < 5 else 5

        # No matches raises a exception
        if level == 0:
            raise LevelNotFound

        # Save the anchor
        self._anchors["level"] = (
            (
                min([pt[0] for pt in marker]) + sub[0][0],
                min([pt[1] for pt in marker]) + sub[0][1]
            ),
            (
                max([pt[0] for pt in marker]) + w + sub[0][0],
                max([pt[1] for pt in marker]) + h + sub[0][1]
            )
        )

        return level

    def _find_time(self) -> datetime.time:
        try:
            gym_image = self._anchors["gym_image"]
            ym = gym_image[1] - gym_image[2] - 10
        except:
            ym = 60

        for x in [
            0.2,
            (-0.2, 1.0),
            1.0
        ]:
            sub = self._calc_subset(x, (0, ym))
            img = self._subset(sub)
            img = cv2.GaussianBlur(img, (5, 5), 3)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

            if ScreenshotRaid.debug:
                self._image_sections["time"] = img

            text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

            logging.debug(text)

            result = re.search(r"([0-2]?[0-9]):([0-5][0-9])", text)

            try:
                return datetime.time(int(result.group(1)), int(result.group(2)))
            except:
                pass

        raise TimeNotFound

    def _find_anchors(self) -> None:
        ANCHORS = {
            "gym_image": [
                ((0, 0.25), (40, 0.20)),
                {"param1": 50, "param2": 30, "minRadius": 50, "maxRadius": 65}
            ],
            "gym_detail": [
                ((-0.20, -30), (60, 0.17)),
                {"param1": 50, "param2": 30, "minRadius": 20, "maxRadius": 40}
            ],
            "raid_info": [
                ((30, 0.25), (-250, 1.0)),
                {"param1": 50, "param2": 30, "minRadius": 30, "maxRadius": 40}
            ],
            "exit": [
                (0.25, (-250, 1.0)),
                {"param1": 50, "param2": 30, "minRadius": 30, "maxRadius": 40}
            ],
            "gym": [
                ((-0.25, -30), (-250, 1.0)),
                {"param1": 50, "param2": 30, "minRadius": 30, "maxRadius": 40}
            ]
        }

        # Doesn't search anchors are already found
        for a in self._anchors:
            ANCHORS.pop(a, None)

        for a in ANCHORS:
            sub = self._calc_subset(ANCHORS[a][0])
            img = self._subset(sub)
            circles = cv2.HoughCircles(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1.2, 100,
                                       **ANCHORS[a][1])
            if circles is None:
                self._anchors[a] = None
                continue

            x, y, r = np.round(circles[0]).astype("int")[0]

            x += sub[0][0]
            y += sub[0][1]

            self._anchors_available += 1
            self._anchors[a] = (x, y, r)

    @property
    @CachedMethod
    def hatching_timer_position(self) -> Union[Rect, None]:
        try:
            self._anchors["hatching_timer"] = self._find_hatching_timer()
            return self._anchors["hatching_timer"]
        except HatchingTimerNotFound:
            return None

    @property
    @CachedMethod
    def raid_timer_position(self) -> Union[Rect, None]:
        try:
            self._anchors["raid_timer"] = self._find_raid_timer()
            return self._anchors["raid_timer"]
        except RaidTimerNotFound:
            return None

    @property
    @CachedMethod
    def ex_tag_position(self) -> Union[Rect, None]:
        try:
            return self._find_ex_tag()
        except ExTagNotFound:
            return None

    @property
    @CachedMethod
    def timer(self) -> Union[datetime.timedelta, None]:
        return self.hatching_timer if self.is_egg else self.raid_timer

    @property
    @CachedMethod
    def hatching_timer(self) -> Union[datetime.timedelta, None]:
        try:
            return self._read_hatching_timer()
        except HatchingTimerException:
            return None

    @property
    @CachedMethod
    def raid_timer(self) -> Union[datetime.timedelta, None]:
        try:
            return self._read_raid_timer()
        except RaidTimerException:
            return None

    @property
    @CachedMethod
    def gym(self) -> Union[Gym, None]:
        try:
            return self._find_gym()
        except GymNotFound:
            return None

    @property
    @CachedMethod
    def boss(self) -> Union[Boss, None]:
        try:
            return self._find_boss()
        except (BossesListNotAvailable, BossNotFound):
            return None

    @property
    @CachedMethod
    def is_ex(self) -> bool:
        try:
            if self._check_ex_tag():
                self._anchors["ex_tag"] = self.ex_tag_position
                return True
        except ExTagException:
            return False

    @property
    @CachedMethod
    def level(self) -> Union[int, None]:
        try:
            return self._find_level()
        except LevelNotFound:
            return None

    @property
    @CachedMethod
    def time(self) -> Union[datetime.time, None]:
        try:
            return None
            # The calc of the time from the notification bar is momentary disabled
            # return self._find_time()
        except TimeNotFound:
            return None

    @property
    @CachedMethod
    def is_raid(self) -> bool:
        # If there are not at least 4 anchors the screenshot is not a raid
        if self._anchors_available < 4:
            return False

        # Try to find the hatching timer
        if self.hatching_timer_position is not None:
            return True

        # Try to find the raid timer
        if self.raid_timer_position is not None:
            return True

        # If there is neither hatching timer nor raid timer then the screenshot is not a raid
        return False

    @property
    @CachedMethod
    def is_egg(self) -> bool:
        return self.hatching_timer is not None

    @property
    @CachedMethod
    def is_hatched(self) -> bool:
        return self.hatching_timer is None

    @property
    @CachedMethod
    def hatching(self) -> Union[datetime.time, None]:
        if self.hatching_timer is None:
            return None

        if self.time is not None:
            return (datetime.datetime.combine(datetime.date(1970, 1, 1), self.time) + self.hatching_timer).time()
        else:
            return (datetime.datetime.now() + self.hatching_timer).time()

    @property
    @CachedMethod
    def end(self) -> Union[datetime.time, None]:
        # Get time or use system time
        time = datetime.datetime.combine(datetime.date(1970, 1, 1), self.time) \
            if self.time is not None else datetime.datetime.now()

        if self.is_hatched:
            if self.raid_timer is not None:
                return (time + self.raid_timer).time()
            else:
                return None
        else:
            if self.hatching_timer is not None:
                return (time + self.hatching_timer + datetime.timedelta(minutes=45)).time()
            else:
                return None

    def to_raid(self) -> Raid:
        if self.is_hatched:
            return Raid(gym=self.gym,
                        level=self.level,
                        end=self.end,
                        boss=self.boss,
                        is_hatched=True,
                        is_ex=self.is_ex,
                        is_aprx_time=(True if self.time is None else False))
        else:
            return Raid(gym=self.gym,
                        level=self.level,
                        hatching=self.hatching,
                        end=self.end,
                        is_hatched=False,
                        is_ex=self.is_ex,
                        is_aprx_time=(True if self.time is None else False))

    def _get_anchors_image(self) -> np.ndarray:
        img = self._img.copy()
        for i in self._anchors.values():
            try:
                if len(i) == 3:
                    cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
                    cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
                elif len(i) == 2:
                    cv2.rectangle(img, i[0], i[1], (0, 255, 0), 2)
            except Exception:
                pass

        return img
