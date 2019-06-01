import cv2

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
