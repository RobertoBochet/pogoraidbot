import logging
import re
from functools import reduce
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

        # cv2.imshow("a",self._img);cv2.waitKey(1000)
        # DEBUG
        self._sub = []

        self._find_anchors()

    def _calc_subset(self, *subs):
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

        # logging.debug("request {} calc {} size {}".format(subs, (tuple(points[0]), tuple(points[1])), self._size))

        return (tuple(points[0]), tuple(points[1]))

    def _subset(self, rect):
        return self._img[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]

    def get_hatching_timer_position(self):
        try:
            if self._anchors["hatching_timer"] is not None:
                return self._anchors["hatching_timer"]
            else:
                raise HatchingTimerNotFound
        except (AttributeError, KeyError):
            pass
        self._anchors["hatching_timer"] = None
        self._anchors["hatching_timer"] = self._find_hatching_timer()
        return self._anchors["hatching_timer"]

    def _find_hatching_timer(self):
        red_lower = numpy.array([150, 100, 230])
        red_upper = numpy.array([255, 130, 255])

        sub = self._calc_subset(0.35, (0.15, 0.29))

        img = self._subset(sub)
        img = cv2.GaussianBlur(img, (5, 5), 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(img, red_lower, red_upper)

        self._hatching_timer_img = mask  # TODO debug

        try:
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            x, y, w, h = cv2.boundingRect(
                reduce((lambda x, y: x if cv2.contourArea(x) > cv2.contourArea(y) else y), contours))

            return ((sub[0][0] + x, sub[0][1] + y), (sub[0][0] + x + w, sub[0][1] + y + h))
        except:
            pass
        raise HatchingTimerNotFound

    def get_hatching_timer(self):
        try:
            if self._hatching_timer is not None:
                return self._hatching_timer
            else:
                raise HatchingTimerUnreadable
        except AttributeError:
            pass
        self._hatching_timer = None
        self._hatching_timer = self._read_hatching_timer()
        return self._hatching_timer

    def _read_hatching_timer(self):
        img = self._subset(self.get_hatching_timer_position())
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY_INV)

        self._hatching_timer_img = img  # TODO debug

        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        result = re.search(r"([0-3]):([0-5][0-9]):([0-5][0-9])", text)

        try:
            return (int(result.group(1)), int(result.group(2)), int(result.group(3)))
        except Exception:
            pass
        raise HatchingTimerUnreadable

    def get_raid_timer_position(self):
        try:
            if self._anchors["raid_timer"] is not None:
                return self._anchors["raid_timer"]
            else:
                raise RaidTimerNotFound
        except (AttributeError, KeyError):
            pass
        self._anchors["raid_timer"] = None
        self._anchors["raid_timer"] = self._find_raid_timer()
        return self._anchors["raid_timer"]

    def _find_raid_timer(self):
        red_lower = numpy.array([-50, 175, 230])
        red_upper = numpy.array([50, 205, 255])

        sub = self._calc_subset(((-0.30, -0.02), (0.54, 0.65)))

        img = self._subset(sub)
        img = cv2.GaussianBlur(img, (5, 5), 5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(img, red_lower, red_upper)

        self._raid_timer_img = mask  # TODO debug

        try:
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            x, y, w, h = cv2.boundingRect(
                reduce((lambda x, y: x if cv2.contourArea(x) > cv2.contourArea(y) else y), contours))

            return ((sub[0][0] + x, sub[0][1] + y), (sub[0][0] + x + w, sub[0][1] + y + h))
        except:
            pass
        raise RaidTimerNotFound

    def get_raid_timer(self):
        try:
            if self._raid_timer is not None:
                return self._raid_timer
            else:
                raise RaidTimerUnreadable
        except AttributeError:
            pass
        self._raid_timer = None
        self._raid_timer = self._read_raid_timer()
        return self._raid_timer

    def _read_raid_timer(self):
        img = self._subset(self.get_raid_timer_position())
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        __, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY_INV)

        self._raid_timer_img = img  # TODO debug

        text = pytesseract.image_to_string(img, config=('--oem 1 --psm 3'))

        result = re.search(r"([0-3]):([0-5][0-9]):([0-5][0-9])", text)

        try:
            return (int(result.group(1)), int(result.group(2)), int(result.group(3)))
        except Exception:
            pass
        raise RaidTimerUnreadable

    def get_timer(self):
        return self.get_hatching_timer() if self.is_egg() else self.get_raid_timer()

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

    def get_level(self):
        try:
            if self._level is not None:
                return self._level
            else:
                raise LevelNotFound
        except AttributeError:
            pass
        self._level = None
        self._level = self._find_level()
        return self._level

    def _find_level(self):
        if self.is_egg():
            ht_pos = self.get_hatching_timer_position()
            sub = ((ht_pos[0][0] - 60, ht_pos[1][1] + 25), (ht_pos[1][0] + 60, ht_pos[1][1] + 95))
        else:
            sub = self._calc_subset(0.5, (0.10, 0.20))  # TODO improve subset in raid for level

        img = self._subset(sub)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (3, 3), 3)
        __, img = cv2.threshold(img, 252, 255, cv2.THRESH_BINARY)
        img = cv2.resize(img, None, fx=1 / 4, fy=1 / 4, interpolation=cv2.INTER_LINEAR)
        img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR)
        __, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        img = cv2.dilate(img, None, iterations=6)

        contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(filter((lambda x: cv2.contourArea(x) > 400), contours))

        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img = cv2.drawContours(img, contours, -1, (255, 0, 0), 2)

        self._level_img = img

        return len(contours)

        raise LevelNotFound  # TODO find a method to detect error

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
            sub = self._calc_subset(ANCHORS[a][0])
            img = self._subset(sub)
            circles = cv2.HoughCircles(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1.2, 100,
                                       **ANCHORS[a][1])
            if circles is None:
                self._anchors[a] = None
                continue

            x, y, r = numpy.round(circles[0]).astype("int")[0]

            x += sub[0][0]
            y += sub[0][1]

            self._anchors_available += 1
            self._anchors[a] = (x, y, r)

    def _get_anchors_image(self):
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

    def is_egg(self):
        try:
            self.get_hatching_timer()
            return True
        except HatchingTimerException:
            return False

    def is_hatched(self):
        return not self.is_egg()

    def compute(self):
        processes = [
            Process(target=self._find_hours),
            Process(target=self._find_hatching_timer)
        ]

        for p in processes:
            p.start()

        for p in processes:
            p.join()
