import logging
import time

from millify import prettify

from TwitchChannelPointsMiner.classes.entities.Bet import BetSettings
from TwitchChannelPointsMiner.classes.entities.Stream import Stream
from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.constants.twitch import URL

logger = logging.getLogger(__name__)


class StreamerSettings(object):
    def __init__(
        self,
        make_predictions: bool = True,
        follow_raid: bool = True,
        claim_drops: bool = True,
        watch_streak: bool = True,
        bet: BetSettings = BetSettings(),
    ):
        self.make_predictions = make_predictions
        self.follow_raid = follow_raid
        self.claim_drops = claim_drops
        self.watch_streak = watch_streak
        self.bet = bet


class Streamer(object):
    def __init__(self, username, settings=None):
        self.username = username.lower().strip()
        self.channel_id = 0
        self.settings = settings
        self.is_online = False
        self.stream_up = 0
        self.online_at = 0
        self.offline_at = 0
        self.channel_points = 0
        self.minute_watched_requests = None
        self.viewer_is_mod = False

        self.stream = Stream()

        self.raid = None
        self.history = {}

        self.streamer_url = f"{URL}/{self.username}"
        self.chat_url = f"{URL}/popout/{self.username}/chat?popout="

    def __repr__(self):
        return f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={prettify(self.channel_points, '.')})"

    def __str__(self):
        return (
            f"{self.username} ({prettify(self.channel_points, '.')} points)"
            if Settings.logger.less
            else self.__repr__()
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
            self.stream.watch_streak_missing = False

    def stream_up_elapsed(self):
        return self.stream_up == 0 or ((time.time() - self.stream_up) > 120)
