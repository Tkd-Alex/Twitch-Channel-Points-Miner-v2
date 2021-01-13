import logging
import threading
import signal
import sys
import time
import os
import uuid
import copy
import emoji

from datetime import datetime
from pathlib import Path

from TwitchChannelPointsMiner.classes.WebSocketsPool import WebSocketsPool
from TwitchChannelPointsMiner.classes.PubsubTopic import PubsubTopic
from TwitchChannelPointsMiner.classes.Streamer import Streamer
from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.Bet import Strategy
from TwitchChannelPointsMiner.classes.TwitchBrowser import TwitchBrowser, Browser
from TwitchChannelPointsMiner.classes.Exceptions import StreamerDoesNotExistException

logging.getLogger("urllib3").setLevel(
    logging.ERROR
)  # Suppress warning for urllib3.connectionpool (selenium close connection)

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
        save_logs: bool = True,
        browser: Browser = Browser.FIREFOX,
        show_browser: bool = False,
        do_browser_screenshot: bool = False,
        bet_strategy: Strategy = Strategy.SMART,
        bet_percentage: int = 5,
        bet_percentage_gap: int = 20,
        bet_max_points: int = 50000,
    ):
        self.twitch = Twitch(username)
        self.twitch_browser = False
        self.follow_raid = follow_raid
        self.streamers = []
        self.minute_watcher_thread = None
        self.ws_pool = None

        self.make_predictions = make_predictions
        self.browser = browser
        self.show_browser = show_browser
        self.do_browser_screenshot = do_browser_screenshot

        self.bet_strategy = bet_strategy
        self.bet_percentage = bet_percentage
        self.bet_percentage_gap = bet_percentage_gap
        self.bet_max_points = bet_max_points

        self.session_id = str(uuid.uuid4())
        self.running = False
        self.start_datetime = None
        self.original_streamers = []

        if save_logs is True:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            logs_path = os.path.join(Path().absolute(), "logs")
            Path(logs_path).mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(
                os.path.join(
                    logs_path,
                    f"{username}.{datetime.now().strftime('%d-%m-%Y-%H:%M:%S')}.log",
                )
            )
            formatter = logging.Formatter(logging_format)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        signal.signal(signal.SIGINT, self.end)
        signal.signal(signal.SIGSEGV, self.end)
        signal.signal(signal.SIGTERM, self.end)

    def mine(self, streamers: list = []):
        self.run(streamers)

    def run(self, streamers: list = []):
        if self.running:
            logger.error("You can't start multiple session of this istance!")
        else:
            logger.info(
                emoji.emojize(
                    f":bomb:  Start session: {self.session_id}", use_aliases=True
                )
            )
            self.running = True
            self.start_datetime = datetime.now()

            self.twitch.login()

            for streamer_username in streamers:
                streamer_username.lower().strip()
                try:
                    channel_id = self.twitch.get_channel_id(streamer_username)
                    streamer = Streamer(streamer_username, channel_id)
                    self.streamers.append(streamer)
                except StreamerDoesNotExistException:
                    logger.info(
                        emoji.emojize(
                            f":cry:  Streamer {streamer_username} does not exist",
                            use_aliases=True,
                        )
                    )

            for streamer in self.streamers:
                self.twitch.load_channel_points_context(streamer)
                self.twitch.check_streamer_online(streamer)
            self.original_streamers = copy.deepcopy(self.streamers)

            if (
                self.make_predictions is True
            ):  # We need a browser to make predictions / bet
                self.twitch_browser = TwitchBrowser(
                    self.twitch.twitch_login.get_auth_token(),
                    self.session_id,
                    bet_strategy=self.bet_strategy,
                    bet_percentage=self.bet_percentage,
                    bet_percentage_gap=self.bet_percentage_gap,
                    bet_max_points=self.bet_max_points,
                    do_screenshot=self.do_browser_screenshot,
                )
                self.twitch_browser.init(show=self.show_browser, browser=self.browser)

            self.minute_watcher_thread = threading.Thread(
                target=self.twitch.send_minute_watched_events, args=(self.streamers,)
            )
            self.minute_watcher_thread.daemon = True
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
                    topics.append(
                        PubsubTopic("predictions-channel-v1", streamer=streamer)
                    )

            for topic in topics:
                self.ws_pool.submit(topic)

            while self.running:
                time.sleep(1.5)

    def end(self, signum, frame):
        # logger.info("Please wait, this operation can take a while ...")
        if self.twitch_browser is not None:
            self.twitch_browser.browser.quit()

        self.running = self.twitch.running = False
        self.ws_pool.end()

        self.__print_report()
        time.sleep(3.5)  # Do sleep for ending browser and threads

        sys.exit(0)

    def __print_report(self):
        print("")
        logger.info(
            emoji.emojize(
                f":electric_plug:  End session '{self.session_id}'", use_aliases=True
            )
        )
        logger.info(
            emoji.emojize(
                f":hourglass:  Duration {datetime.now() - self.start_datetime}",
                use_aliases=True,
            )
        )

        if self.make_predictions:
            logger.info(
                emoji.emojize(
                    f":bar_chart:  Bet settings: Strategy={self.bet_strategy}, Percentage={self.bet_percentage}, Percentage Gap={self.bet_percentage_gap}, Max points={self.bet_max_points}",
                    use_aliases=True,
                )
            )
            print("")

        for streamer_index in range(0, len(self.streamers)):
            logger.info(
                emoji.emojize(
                    f":movie_camera:  {self.streamers[streamer_index]} - Gained: {self.streamers[streamer_index].channel_points - self.original_streamers[streamer_index].channel_points}, Bonus claimed: {self.streamers[streamer_index].bonus_claimed}",
                    use_aliases=True,
                )
            )
