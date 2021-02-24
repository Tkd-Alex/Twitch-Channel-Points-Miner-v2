from enum import Enum, auto


class Priority(Enum):
    ORDER = auto()
    STREAK = auto()
    DROPS = auto()


# Empty object shared between class
class Settings(object):
    __slots__ = ["logger", "streamer_settings"]
