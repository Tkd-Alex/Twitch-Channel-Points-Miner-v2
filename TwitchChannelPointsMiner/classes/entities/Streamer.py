import json
import logging
import os
import time
from threading import Lock

from TwitchChannelPointsMiner.classes.entities.Bet import BetSettings
from TwitchChannelPointsMiner.classes.entities.Stream import Stream
from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.constants import URL
from TwitchChannelPointsMiner.utils import _millify

logger = logging.getLogger(__name__)


class StreamerSettings(object):
    __slots__ = [
        "make_predictions",
        "follow_raid",
        "claim_drops",
        "watch_streak",
        "bet",
    ]

    def __init__(
        self,
        make_predictions: bool = None,
        follow_raid: bool = None,
        claim_drops: bool = None,
        watch_streak: bool = None,
        bet: BetSettings = None,
    ):
        self.make_predictions = make_predictions
        self.follow_raid = follow_raid
        self.claim_drops = claim_drops
        self.watch_streak = watch_streak
        self.bet = bet

    def default(self):
        for name in ["make_predictions", "follow_raid", "claim_drops", "watch_streak"]:
            if getattr(self, name) is None:
                setattr(self, name, True)
        if self.bet is None:
            self.bet = BetSettings()

    def __repr__(self):
        return f"BetSettings(make_predictions={self.make_predictions}, follow_raid={self.follow_raid}, claim_drops={self.claim_drops}, watch_streak={self.watch_streak}, bet={self.bet})"


class Streamer(object):
    __slots__ = [
        "username",
        "channel_id",
        "settings",
        "is_online",
        "stream_up",
        "online_at",
        "offline_at",
        "channel_points",
        "minute_watched_requests",
        "viewer_is_mod",
        "stream",
        "raid",
        "history",
        "streamer_url",
    ]

    def __init__(self, username, settings=None):
        self.username: str = username.lower().strip()
        self.channel_id: str = ""
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

        self.mutex = Lock()

    def __repr__(self):
        return f"Streamer(username={self.username}, channel_id={self.channel_id}, channel_points={_millify(self.channel_points)})"

    def __str__(self):
        return (
            f"{self.username} ({_millify(self.channel_points)} points)"
            if Settings.logger.less
            else self.__repr__()
        )

    def set_offline(self):
        if self.is_online is True:
            self.offline_at = time.time()
            self.is_online = False

        logger.info(
            f"{self} is Offline!",
            extra={
                "emoji": ":sleeping:",
                "color": Settings.logger.color_palette.STREAMER_OFFLINE,
            },
        )

    def set_online(self):
        if self.is_online is False:
            self.online_at = time.time()
            self.is_online = True
            self.stream.init_watch_streak()

        logger.info(
            f"{self} is Online!",
            extra={
                "emoji": ":partying_face:",
                "color": Settings.logger.color_palette.STREAMER_ONLINE,
            },
        )

    def print_history(self):
        return ", ".join(
            [
                f"{key}({self.history[key]['counter']} times, {_millify(self.history[key]['amount'])} gained)"
                for key in sorted(self.history)
                if self.history[key]["counter"] != 0
            ]
        )

    def update_history(self, reason_code, earned, counter=1):
        if reason_code not in self.history:
            self.history[reason_code] = {"counter": 0, "amount": 0}
        self.history[reason_code]["counter"] += counter
        self.history[reason_code]["amount"] += earned

        if reason_code == "WATCH_STREAK":
            self.stream.watch_streak_missing = False

    def stream_up_elapsed(self):
        return self.stream_up == 0 or ((time.time() - self.stream_up) > 120)

    def drops_condition(self):
        return (
            self.settings.claim_drops is True
            and self.is_online is True
            and self.stream.drops_tags is True
            and self.stream.campaigns_ids != []
        )

    # === ANALYTICS === #
    def persistent_points(self, event_type, event_text):
        event_type = event_type.upper()
        if event_type in ["WATCH_STREAK", "WIN", "LOSE"]:
            primary_color = (
                "#45c1ff"
                if event_type == "WATCH_STREAK"
                else ("#ff4560" if event_type == "LOSE" else "#54ff45")
            )
            data = {
                "marker": {
                    "size": 5,
                    "fillColor": "#fff",
                    "strokeColor": primary_color,
                    "radius": 2,
                },
                "label": {
                    "borderColor": primary_color,
                    "offsetY": 0,
                    "style": {
                        "color": "#fff",
                        "background": primary_color,
                    },
                    "text": event_text,
                },
            }
            self.__save_json("points", data)

    def persistent_series(self):
        self.__save_json("series")

    def __save_json(self, key, data={}):
        # https://stackoverflow.com/questions/4676195/why-do-i-need-to-multiply-unix-timestamps-by-1000-in-javascript
        data.update({"x": round(time.time() * 1000), "y": self.channel_points})
        fname = os.path.join(Settings.analytics_path, f"{self.username}.json")
        with self.mutex:
            json_data = json.load(open(fname, "r")) if os.path.isfile(fname) else {}
            if key not in json_data:
                json_data[key] = []

            json_data[key].append(data)
            json.dump(json_data, open(fname, "w"), indent=4)
