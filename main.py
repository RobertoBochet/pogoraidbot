#!/usr/bin/env python3
import glob
import logging
import os
import re
import sys

import cv2

from ScreenshotRaid import ScreenshotRaid


def subset(img, *subs):
    size = (len(img[0]), len(img))

    if len(subs) == 1:
        subs = subs[0]

    subs = list(subs)

    for i in [0, 1]:
        if not isinstance(subs[i], tuple):
            if isinstance(subs[i], float):
                subs[i] = (
                    round((0.5 - subs[i] / 2) * size[i]),
                    round((0.5 + subs[i] / 2) * size[i])
                )
            else:
                subs[i] = (
                    size[i] - round(subs[i] / 2),
                    size[i] - round(subs[i] / 2) + subs[i]
                )
        else:
            subs[i] = (
                round(size[i] * subs[i][0]) if isinstance(subs[i][0], float) else subs[i][0],
                round(size[i] * subs[i][1]) if isinstance(subs[i][1], float) else subs[i][1]
            )

    return img[subs[1][0]:subs[1][1], subs[0][0]:subs[0][1]]


def test_subset(file, img, preprocess):
    for s in preprocess[0]:
        for f in preprocess[1]:
            cv2.imwrite("./sections/{}_{}_{}.png".format(file, s, f), f(subset(img, s)))


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
    try:
        screen.get_raid_timer_position()
        screen.get_hatching_timer_position()
    except:
        pass
    cv2.imwrite("./sections/.ah_{}.png".format(file_name), screen._get_anchors_image())

    try:
        timer = screen.get_raid_timer()
        logging.debug("Raid timer: {}".format(timer))
        cv2.imwrite("./sections/.rt_{}_{}.png".format(timer, file_name), screen._raid_timer_img)
    except Exception:
        cv2.imwrite("./sections/rt_{}.png".format(file_name), screen._raid_timer_img)
        logging.debug("Raid timer: unknown")

    try:
        level = screen.get_level()
        logging.debug("Level: {}".format(level))
        cv2.imwrite("./sections/.l_{}_{}.png".format(level, file_name), screen._level_img)
    except Exception:
        cv2.imwrite("./sections/l_{}.png".format(file_name), screen._level_img)
        logging.debug("Level: unknown")












    '''

    logging.debug("It {} a raid".format("is" if screen.is_raid() else "isn't"))
    logging.debug("It is {}".format("a egg" if screen.is_egg() else "hatched"))

    try:
        level = screen.get_level()
        print("Level is {}".format(level))

        cv2.imwrite("./sections/.lv_{}_{}.png".format(level, file_name), screen._level_img)
    except Exception:
        cv2.imwrite("./sections/lv_{}.png".format(file_name), screen._level_img)
        logging.warning("failed")
    '''
    sys.exit(0)

    try:
        gym_name = screen.get_gym_name()
        print("{}".format(gym_name))

        cv2.imwrite("./sections/.gn_{}_{}.png".format(gym_name, file_name), screen._gym_name_img)
    except Exception:
        # test_subset(file_name, img, preprocessing.GYM_NAME)
        traceback.print_exc()

    sys.exit(0)

    try:
        hours, minutes, second = screen.get_raid_timer();
        print("{}:{}:{}".format(hours, minutes, second))

        cv2.imwrite("./sections/.rt_{}:{}:{}_{}.png".format(hours, minutes, second, file_name), screen._raid_timer_img)
    except Exception:
        test_subset(file_name, img, preprocessing.RAID_TIMER)
        traceback.print_exc()

    sys.exit(0)

    try:
        hours, minutes, second = screen.get_hatching_timer();
        print("{}:{}:{}".format(hours, minutes, second))

        cv2.imwrite("./sections/.ht_{}:{}:{}_{}.png".format(hours, minutes, second, file_name),
                    screen._hatching_timer_img)
    except Exception:
        test_subset(file_name, img, preprocessing.HATCHING_TIMER)
        traceback.print_exc()

    try:
        hours, minutes = screen.get_hours();
        print("{}:{}".format(hours, minutes))

        cv2.imwrite("./sections/.t_{}:{}_{}.png".format(hours, minutes, file_name), screen._notice_bar)
    except Exception:
        test_subset(file_name, img, preprocessing.HOURS)
        traceback.print_exc()
