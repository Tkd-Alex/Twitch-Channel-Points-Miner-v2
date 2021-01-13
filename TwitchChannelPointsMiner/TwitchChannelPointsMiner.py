import logging
import threading
import signal
import sys
import time
import os

from pathlib import Path

from TwitchChannelPointsMiner.classes.WebSocketsPool import WebSocketsPool
from TwitchChannelPointsMiner.classes.PubsubTopic import PubsubTopic
from TwitchChannelPointsMiner.classes.Streamer import Streamer
from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.TwitchBrowser import TwitchBrowser, Browser
from TwitchChannelPointsMiner.classes.Exceptions import StreamerDoesNotExistException

logging_format = "%(asctime)s - %(levelname)s - %(name)s - [%(funcName)s]: %(message)s"
logging.basicConfig(
    format=logging_format,
    datefmt="%d/%m/%y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TwitchChannelPointsMiner:
    def __init__(
        self,
        username: str,
        make_predictions: bool = True,
        follow_raid: bool = True,
        save_logs: bool = True
    ):
        self.twitch = Twitch(username)
        self.twitch_browser = False
        self.make_predictions = make_predictions
        self.follow_raid = follow_raid
        self.streamers = []
        self.minute_watcher_thread = None
        self.ws_pool = None

        if save_logs is True:
            logs_path = os.path.join(Path().absolute(), "logs")
            Path(logs_path).mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(os.path.join(logs_path, f"{username}.log"))
            formatter = logging.Formatter(logging_format)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        signal.signal(signal.SIGINT, self.end)
        signal.signal(signal.SIGSEGV, self.end)
        signal.signal(signal.SIGTERM, self.end)

    def mine(self, streamers: list = []):
        self.run(streamers)

    def run(self, streamers: list = []):
        self.twitch.login()

        for streamer_username in streamers:
            streamer_username.lower().strip()
            try:
                channel_id = self.twitch.get_channel_id(streamer_username)
                streamer = Streamer(streamer_username, channel_id)
                self.streamers.append(streamer)
            except StreamerDoesNotExistException:
                logger.info(f"😞  Streamer {streamer_username} does not exist")

        for streamer in self.streamers:
            self.twitch.load_channel_points_context(streamer)
            self.twitch.check_streamer_online(streamer)
            # logger.info(streamer)

        if self.make_predictions is True:  # We need a browser to make predictions / bet
            self.twitch_browser = TwitchBrowser(
                self.twitch.twitch_login.get_auth_token()
            )
            self.twitch_browser.init(show=True, browser=Browser.FIREFOX)

        self.minute_watcher_thread = threading.Thread(
            target=self.twitch.send_minute_watched_events, args=(self.streamers,)
        )
        self.minute_watcher_thread.start()

        self.ws_pool = WebSocketsPool(
            twitch=self.twitch,
            twitch_browser=self.twitch_browser,
            streamers=self.streamers,
        )
        topics = [
            PubsubTopic(
                "community-points-user-v1",
                user_id=self.twitch.twitch_login.get_user_id(),
            )
        ]
        if self.make_predictions is True:
            topics.append(
                PubsubTopic(
                    "predictions-user-v1",
                    user_id=self.twitch.twitch_login.get_user_id(),
                )
            )

        for streamer in self.streamers:
            topics.append(PubsubTopic("video-playback-by-id", streamer=streamer))

            if self.follow_raid is True:
                topics.append(PubsubTopic("raid", streamer=streamer))

            if self.make_predictions is True:
                topics.append(PubsubTopic("predictions-channel-v1", streamer=streamer))

        for topic in topics:
            self.ws_pool.submit(topic)

    def end(self):
        if self.twitch_browser is not None:
            self.twitch_browser.browser.close()

        time.sleep(1.5)
        sys.exit(0)
