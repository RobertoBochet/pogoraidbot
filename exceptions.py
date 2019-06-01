class ValueNotFound(Exception):
    pass


class ValueUnreadable(Exception):
    pass


class HoursNotFound(ValueNotFound):
    pass


class TimerNotFound(ValueNotFound):
    pass


class TimerUnreadable(ValueUnreadable):
    pass


class HatchingTimerException(Exception):
    pass


class HatchingTimerNotFound(HatchingTimerException, TimerNotFound):
    pass


class HatchingTimerUnreadable(HatchingTimerException, TimerUnreadable):
    pass


class RaidTimerException(Exception):
    pass


class RaidTimerNotFound(RaidTimerException, TimerNotFound):
    pass


class RaidTimerUnreadable(RaidTimerException, TimerUnreadable):
    pass


class GymNameNotFound(ValueNotFound):
    pass


class LevelNotFound(ValueNotFound):
    pass
