import cv2


def threshold(img, th):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    __, img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY_INV)
    return img


HOURS = [
    [
        (0.2, (0, 40)),
        ((-0.2, 1.0), (0, 40)),
        (1.0, (0, 40)),
        (0.2, (0, 60)),
        ((-0.2, 1.0), (0, 60)),
        (1.0, (0, 60)),
    ],
    [
        lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        lambda img: cv2.GaussianBlur(img, (3, 3), 0),
        lambda img: cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC),
        lambda img: img
    ]
]

HATCHING_TIMER = [
    [
        (0.27, (0.195, 0.245)),
        (0.27, (0.22, 0.27)),
        (0.27, (0.25, 0.29))
    ],
    [
        lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        lambda img: threshold(img, 210)
    ]
]

RAID_TIMER = [
    [
        ((-0.26, -0.06), (0.55, 0.59)),
        ((-0.26, -0.06), (0.59, 0.635)),
        ((-0.26, -0.06), (0.575, 0.605)),
        #((-0.26, -0.06), (0.55, 0.635))
    ],
    [
        lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        lambda img: threshold(img, 210)
    ]
]

GYM_NAME = [
    [
        ((.18, 0.91), (60, 200))
    ],
    [
        lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        #lambda img: threshold(img, 210)
    ]
]
