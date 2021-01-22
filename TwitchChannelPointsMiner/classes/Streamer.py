import time
import logging

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(self, username, channel_id, less_printing: bool = False):
        self.username = username
        self.channel_id = channel_id
        self.is_online = False
        self.online_at = 0
        self.offline_at = 0
        self.channel_points = 0
        self.minute_watched_requests = None
        self.raid = None
        self.history = {}

        self.streamer_url = f"https://www.twitch.tv/{self.username}"
        self.chat_url = f"https://www.twitch.tv/popout/{self.username}/chat?popout="

        self.less_printing = less_printing

    def __repr__(self):
        return (
            f"Streamer: {self.username}"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={self.channel_points})"
        )

    def __str__(self):
        return (
            f"Streamer: {self.username}"
            if self.less_printing is True
            else f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={self.channel_points})"
        )

    def set_offline(self):
        self.offline_at = time.time()
        self.is_online = False
        logger.info(f"{self} is Offline!", extra={"emoji": ":sleeping:"})

    def set_online(self):
        self.online_at = time.time()
        self.is_online = True
        logger.info(f"{self} is Online!", extra={"emoji": ":partying_face:"})

    def print_history(self):
        return ", ".join(
            [
                f"{key}({self.history[key]['counter']} times, {self.history[key]['amount']} gained)"
                for key in self.history
            ]
        )

    def update_history(self, reason_code, earned):
        if reason_code not in self.history:
            self.history[reason_code] = {"counter": 0, "amount": 0}
        self.history[reason_code]["counter"] += 1
        self.history[reason_code]["amount"] += earned

    def set_less_printing(self, value):
        self.less_printing = value