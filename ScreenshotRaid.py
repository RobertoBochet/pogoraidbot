import logging
import re
from multiprocessing import Process

import cv2
import numpy
import pytesseract

import preprocessing
from exceptions import *


class ScreenshotRaid:
    def __init__(self, img):
        self._img = img
        self._size = (len(self._img[0]), len(self._img))

        # DEBUG
        self._sub = []

        self._find_anchors()

    def _calc_subset(self, *subs):
        if len(subs) == 1:
            subs = subs[0]

        subs = list(subs)

        for i in [0, 1]:
            if not isinstance(subs[i], tuple):
                if isinstance(subs[i], float):
                    subs[i] = (
                        round((0.5 - subs[i] / 2) * self._size[i]),
                        round((0.5 + subs[i] / 2) * self._size[i])
                    )
                else:
                    subs[i] = (
                        self._size[i] - round(subs[i] / 2),
                        self._size[i] - round(subs[i] / 2) + subs[i]
                    )
            else:
                subs[i] = (
                    round(self._size[i] * subs[i][0]) if isinstance(subs[i][0], float) else subs[i][0],
                    round(self._size[i] * subs[i][1]) if isinstance(subs[i][1], float) else subs[i][1]
                )

            subs[i] = (
                subs[i][0] + self._size[i] if subs[i][0] < 0 else subs[i][0],
                subs[i][1] + self._size[i] if subs[i][1] < 0 else subs[i][1]
            )

        return subs

    def _subset(self, *subs):

        subs = self._calc_subset(*subs)

        return self._img[subs[1][0]:subs[1][1], subs[0][0]:subs[0][1]]

    def _find_hours(self):
        rx = re.compile(r"([0-2]?[0-9]):([0-5][0-9])")

        for sub in preprocessing.HOURS[0]:
            for func in preprocessing.HOURS[1]:
                img = func(self._subset(sub))
                text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

                logging.debug(text)

                result = rx.search(text)

                self._notice_bar = img

                if result is not None:
                    return (int(result.group(1)), int(result.group(2)))

        self._hours = None
        raise HoursNotFound

    def _find_hatching_timer(self):
        rx = re.compile(r"([0-3]):([0-5][0-9]):([0-5][0-9])")

        for sub in preprocessing.HATCHING_TIMER[0]:
            for func in preprocessing.HATCHING_TIMER[1]:
                img = func(self._subset(sub))
                text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

                logging.debug(text)

                result = rx.search(text)

                self._hatching_timer_img = img

                if result is not None:
                    return (int(result.group(1)), int(result.group(2)), int(result.group(3)))

        self._hatching_timer = None
        raise HatchingTimerNotFound

    def _find_raid_timer(self):
        rx = re.compile(r"([0-3]):([0-5][0-9]):([0-5][0-9])")

        for sub in preprocessing.RAID_TIMER[0]:
            for func in preprocessing.RAID_TIMER[1]:
                img = func(self._subset(sub))
                text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

                logging.debug(text)

                result = rx.search(text)

                self._raid_timer_img = img

                if result is not None:
                    return (int(result.group(1)), int(result.group(2)), int(result.group(3)))

        self._raid_timer = None
        raise RaidTimerNotFound

    def _find_gym_name(self):
        circle_img = self._subset((0, 0.30), (0, 0.20))

        circles = cv2.HoughCircles(cv2.cvtColor(circle_img, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1.2, 100,
                                   param1=50, param2=30, minRadius=50, maxRadius=65)

        if circles is not None:
            x, y, r = numpy.round(circles[0]).astype("int")[0]

            img = self._subset((x + r + 10, -160), (y - r + 5, y + r - 5))
        else:
            img = self._subset((200, -160), (60, 150))

        img = preprocessing.threshold(img, 220)
        text = pytesseract.image_to_string(img, config=('-l ita --oem 1 --psm 3'))

        text = text.rstrip().replace('\n', ' ')
        text = " ".join(text.split())

        logging.debug(text)

        self._gym_name_img = img

        return text
        # TODO add the exception case

    def get_hours(self):
        try:
            if self._hours is not None:
                return self._hours
            else:
                raise HoursNotFound
        except AttributeError:
            pass
        self._hours = self._find_hours()
        return self._hours

    def get_hatching_timer(self):
        try:
            if self._hatching_timer is not None:
                return self._hatching_timer
            else:
                raise HatchingTimerNotFound
        except AttributeError:
            pass
        self._hatching_timer = self._find_hatching_timer()
        return self._hatching_timer

    def get_raid_timer(self):
        try:
            if self._raid_timer is not None:
                return self._raid_timer
            else:
                raise RaidTimerNotFound
        except AttributeError:
            pass
        self._raid_timer = self._find_raid_timer()
        return self._raid_timer

    def get_gym_name(self):
        try:
            if self._gym_name is not None:
                return self._gym_name
            else:
                raise GymNameNotFound
        except AttributeError:
            pass
        self._gym_name = self._find_gym_name()
        return self._gym_name

    def _find_anchors(self):
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

        self._anchors = {}
        self._anchors_available = 0

        for a in ANCHORS:
            self._sub.append(self._calc_subset(ANCHORS[a][0]))
            img = self._subset(ANCHORS[a][0])
            circles = cv2.HoughCircles(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1.2, 100,
                                       **ANCHORS[a][1])
            if circles is None:
                self._anchors[a] = None
                continue

            x, y, r = numpy.round(circles[0]).astype("int")[0]

            subset = self._calc_subset(ANCHORS[a][0])

            x += subset[0][0]
            y += subset[1][0]

            if subset[0][0] < 0:
                x += self._size[0]
            if subset[1][0] < 0:
                y += self._size[1]

            self._anchors_available += 1
            self._anchors[a] = (x, y, r)

    def _get_anchors_image(self):
        img = self._img.copy()
        for i in self._anchors.values():
            if i is None:
                continue
            cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
            logging.debug(i)

        for i in self._sub:
            print(i)
            cv2.rectangle(img, (i[0][0], i[1][0]), (i[0][1], i[1][1]), (255, 0, 0), 2)

        return img

    def is_raid(self):
        try:
            return True if self._anchors_available >= 4 else False
        except AttributeError:
            pass
        self._find_anchors()
        return True if self._anchors_available >= 4 else False

    def compute(self):
        processes = [
            Process(target=self._find_hours),
            Process(target=self._find_hatching_timer)
        ]

        for p in processes:
            p.start()

        for p in processes:
            p.join()
