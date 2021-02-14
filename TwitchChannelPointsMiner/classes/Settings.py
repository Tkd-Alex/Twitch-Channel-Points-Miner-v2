import json


class Settings(object):
    __slots__ = ["logger", "streamer_settings"]
    streamers_settings = []

    @classmethod
    def write(cls, fname):
        with open(fname, "w") as fp:
            json.dump(cls.streamers_settings, fp, sort_keys=True, indent=4)

    @classmethod
    def append(cls, streamer):
        cls.streamers_settings.append(
            {
                "username": streamer.username,
                "settings": None
                if streamer.settings is None
                else streamer.settings.to_dict(),
            }
        )

    @staticmethod
    def parse(data):
        return None

    @staticmethod
    def read(fname):
        return json.load(open(fname, "r"))
