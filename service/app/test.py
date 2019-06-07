#!/usr/bin/env python3
import glob
import logging
import os
import re
import sys

import cv2

from screenshot import ScreenshotRaid

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) is not 2:
        print("error")
        sys.exit(1)

    file_rx = re.compile(r"^(?:.+\/)?([^\/\.]+)(?:\.(?:[^\.\/]+))?$")
    file_path = sys.argv[1]
    file_name = file_rx.match(file_path)

    if file_name is None:
        print("error")
        sys.exit(1)

    file_name = file_name.group(1)

    img = cv2.imread(file_path, cv2.IMREAD_COLOR)

    file_notice_bar = "{}_notice.png".format(file_name)

    for file in glob.glob("./sections/*{}*".format(file_name)) + glob.glob("./sections/.*{}*".format(file_name)):
        os.remove(file)

    screen = ScreenshotRaid(img)

    logging.debug("Is a raid: {}".format(screen.is_raid()))

    if not screen.is_raid():
        sys.exit(1)

    logging.debug("Is a egg: {}".format(screen.is_egg()))

    try:
        time = screen.get_time()
        logging.debug("Time: {}:{}".format(*time))
        cv2.imwrite("./sections/.t_{}_{}.png".format(time, file_name), screen._time_img)
    except Exception:
        cv2.imwrite("./sections/t_{}.png".format(file_name), screen._time_img)
        logging.debug("Time: unknown")

    try:
        gym_name = screen.get_gym_name()
        logging.debug("Gym name: {}".format(gym_name))
        cv2.imwrite("./sections/.gn_{}_{}.png".format(gym_name, file_name), screen._gym_name_img)
    except Exception:
        cv2.imwrite("./sections/gn_{}.png".format(file_name), screen._gym_name_img)
        logging.debug("Gym name: unknown")

    try:
        timer = screen.get_timer()
        logging.debug("Timer: {}:{}:{}".format(*timer))
        cv2.imwrite("./sections/.tr_{}_{}.png".format(timer, file_name),
                    screen._hatching_timer_img if screen.is_egg() else screen._raid_timer_img)
    except Exception:
        cv2.imwrite("./sections/tr_{}.png".format(file_name),
                    screen._hatching_timer_img if screen.is_egg() else screen._raid_timer_img)
        logging.debug("Timer: unknown")

    try:
        level = screen.get_level()
        logging.debug("Level: {}".format(level))
        cv2.imwrite("./sections/.l_{}_{}.png".format(level, file_name), screen._level_img)
    except Exception:
        cv2.imwrite("./sections/l_{}.png".format(file_name), screen._level_img)
        logging.debug("Level: unknown")

    cv2.imwrite("./sections/.ah_{}.png".format(file_name), screen._get_anchors_image())
