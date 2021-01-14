import time
import logging
import emoji

logger = logging.getLogger(__name__)


class Streamer:
    def __init__(
        self,
        username,
        channel_id,
    ):
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

    def __repr__(self):
        return f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={self.channel_points})"

    def set_offline(self):
        self.offline_at = time.time()
        self.is_online = False
        logger.info(emoji.emojize(f":sleeping:  {self} is Offline!", use_aliases=True))

    def set_online(self):
        self.online_at = time.time()
        self.is_online = True
        logger.info(
            emoji.emojize(f":partying_face:  {self} is Online!", use_aliases=True)
        )

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
