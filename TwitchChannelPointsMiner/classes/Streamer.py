import logging
import time

from TwitchChannelPointsMiner.utils import millify

from TwitchChannelPointsMiner.classes.Stream import Stream
from TwitchChannelPointsMiner.constants.twitch import URL

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, username, channel_id, less_printing: bool = False):
        self.username = username
        self.channel_id = channel_id
        self.is_online = False
        self.stream_up = 0
        self.online_at = 0
        self.offline_at = 0
        self.channel_points = 0
        self.minute_watched_requests = None
        self.viewer_is_mod = False

        self.stream = Stream(less_printing=less_printing)

        self.raid = None
        self.history = {}

        self.streamer_url = f"{URL}/{self.username}"
        self.chat_url = f"{URL}/popout/{self.username}/chat?popout="

        self.less_printing = less_printing

    def __repr__(self):
        return (
            f"{self.username} ({millify(self.channel_points)} points)"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={millify(self.channel_points)})"
        )

    def __str__(self):
        return (
            f"{self.username} ({millify(self.channel_points)} points)"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={millify(self.channel_points)})"
        )

    def set_offline(self):
        if self.is_online is True:
            self.offline_at = time.time()
            self.is_online = False

        logger.info(f"{self} is Offline!", extra={"emoji": ":sleeping:"})

    def set_online(self):
        if self.is_online is False:
            self.online_at = time.time()
            self.is_online = True
            self.stream.init_watch_streak()

        logger.info(f"{self} is Online!", extra={"emoji": ":partying_face:"})

    def print_history(self):
        return ", ".join(
            [
                f"{key}({self.history[key]['counter']} times, {millify(self.history[key]['amount'])} gained)"
                for key in self.history
            ]
        )

    def update_history(self, reason_code, earned):
        if reason_code not in self.history:
            self.history[reason_code] = {"counter": 0, "amount": 0}
        self.history[reason_code]["counter"] += 1
        self.history[reason_code]["amount"] += earned

        if reason_code == "WATCH_STREAK":
            self.stream.watch_streak_missing = False

    def set_less_printing(self, value):
        self.less_printing = value

    def stream_up_elapsed(self):
        return self.stream_up == 0 or ((time.time() - self.stream_up) > 120)
