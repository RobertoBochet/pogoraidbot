class ValueNotFound(Exception):
    pass


class ValueUnreadable(Exception):
    pass


class HoursNotFound(ValueNotFound):
    pass


class HatchingTimerException(Exception):
    pass


class HatchingTimerNotFound(HatchingTimerException, ValueNotFound):
    pass


class HatchingTimerUnreadable(HatchingTimerException, ValueUnreadable):
    pass


class RaidTimerNotFound(ValueNotFound):
    pass


class GymNameNotFound(ValueNotFound):
    pass


class LevelNotFound(ValueNotFound):
    pass
