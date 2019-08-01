class ValueNotFound(Exception):
    pass


class ValueUnreadable(Exception):
    pass


class TimeNotFound(ValueNotFound):
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


class ExTagException(Exception):
    pass


class ExTagNotFound(ExTagException, ValueNotFound):
    pass


class ExTagUnreadable(ExTagException, ValueUnreadable):
    pass


class GymNameNotFound(ValueNotFound):
    pass


class LevelNotFound(ValueNotFound):
    pass


class PokemonRaidsListNotAvailable(Exception):
    pass


class BossNotFound(ValueNotFound):
    pass
