import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings(object):
    __slots__ = ["logger", "streamer_settings"]
    streamers_settings = []

    @classmethod
    def write(cls, fname):
        fname = (
            fname
            if fname is not None
            else os.path.join(Path().absolute(), "streamers.json")
        )
        if fname.endswith(".json") is False:
            fname += ".json"
        if cls.streamers_settings != cls.read(fname):
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

    # Get StreamerSettings as args, prevent circular imports
    @staticmethod
    def parse(data, StreamerSettings):
        return None if data is None else StreamerSettings.from_dict(data)

    @staticmethod
    def read(fname):
        try:
            if fname.endswith(".json") is False:
                fname += ".json"
            return json.load(open(fname, "r")) if os.path.isfile(fname) else []
        except json.decoder.JSONDecodeError:
            logger.error(f"Failed to read {fname}", exc_info=True)
            return []
