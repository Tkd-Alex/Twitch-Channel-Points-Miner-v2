import time
import logging

from millify import prettify

from TwitchChannelPointsMiner.constants import TWITCH_URL

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

        self.__init_watch_streak()

        self.raid = None
        self.history = {}

        self.streamer_url = f"{TWITCH_URL}/{self.username}"
        self.chat_url = f"{TWITCH_URL}/popout/{self.username}/chat?popout="

        self.less_printing = less_printing

    def __repr__(self):
        return (
            f"{self.username} ({prettify(self.channel_points, '.')} points)"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={prettify(self.channel_points, '.')})"
        )

    def __str__(self):
        return (
            f"{self.username} ({prettify(self.channel_points, '.')} points)"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={prettify(self.channel_points, '.')})"
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
            self.__init_watch_streak()

        logger.info(f"{self} is Online!", extra={"emoji": ":partying_face:"})

    def update_minute_watched(self):
        if self.minute_watched_timestamp != 0:
            self.minute_watched += round(
                (time.time() - self.minute_watched_timestamp) / 60, 5
            )
        self.minute_watched_timestamp = time.time()

    def print_history(self):
        return ", ".join(
            [
                f"{key}({self.history[key]['counter']} times, {prettify(self.history[key]['amount'], '.')} gained)"
                for key in self.history
            ]
        )

    def update_history(self, reason_code, earned):
        if reason_code not in self.history:
            self.history[reason_code] = {"counter": 0, "amount": 0}
        self.history[reason_code]["counter"] += 1
        self.history[reason_code]["amount"] += earned

        if reason_code == "WATCH_STREAK":
            self.watch_streak_missing = False

    def set_less_printing(self, value):
        self.less_printing = value

    def __init_watch_streak(self):
        self.watch_streak_missing = True
        self.minute_watched = 0
        self.minute_watched_timestamp = 0
