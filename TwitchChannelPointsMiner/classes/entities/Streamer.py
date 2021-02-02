import json
import logging
import os
import time
from threading import Lock

from TwitchChannelPointsMiner.classes.entities.Bet import BetSettings
from TwitchChannelPointsMiner.classes.entities.Stream import Stream
from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.constants.twitch import URL
from TwitchChannelPointsMiner.utils import _millify

logger = logging.getLogger(__name__)


class StreamerSettings(object):
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
        return f"BetSettings(MakePredictions={self.make_predictions}, FollowRaid={self.follow_raid}, ClaimDrops={self.claim_drops}, WatchStreak={self.watch_streak}, Bet={self.bet})"


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
                f"{key}({self.history[key]['counter']} times, {_millify(self.history[key]['amount'])} gained)"
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

    def persistent_history(self):
        fname = os.path.join(Settings.analytics_path, f"{self.username}.json")
        with self.mutex:
            data = json.load(open(fname)) if os.path.isfile(fname) else []
            # https://stackoverflow.com/questions/4676195/why-do-i-need-to-multiply-unix-timestamps-by-1000-in-javascript
            data.append([round(time.time() * 1000), self.channel_points])
            with open(fname, "w") as outfile:
                json.dump(data, outfile, indent=4)

    def persistent_points(self, event_type, event_text):
        event_type = event_type.upper()
        primary_color = (
            "#45c1ff"
            if event_type == "WATCH_STREAK"
            else ("#ff4560" if event_type == "LOSE" else "#54ff45")
        )
        data = {
            "y": self.channel_points,
            "marker": {
                "size": 4,
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
        self.__save_json("series", {"y": self.channel_points})

    def __save_json(self, key, new_data):
        fname = os.path.join(Settings.analytics_path, f"{self.username}.json")
        with self.mutex:
            data = json.load(open(fname)) if os.path.isfile(fname) else {}
            if key not in data:
                data[key] = []

            # https://stackoverflow.com/questions/4676195/why-do-i-need-to-multiply-unix-timestamps-by-1000-in-javascript
            new_data.update({"x": round(time.time() * 1000)})
            data[key].append(new_data)
            with open(fname, "w") as outfile:
                json.dump(data, outfile, indent=4)
