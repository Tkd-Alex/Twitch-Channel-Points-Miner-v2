# -*- coding: utf-8 -*-

import copy
import logging
import random
import signal
import sys
import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime

from TwitchChannelPointsMiner.utils import get_user_agent, _millify
from TwitchChannelPointsMiner.classes.Bet import BetSettings
from TwitchChannelPointsMiner.classes.Exceptions import StreamerDoesNotExistException
from TwitchChannelPointsMiner.classes.Logger import LoggerSettings, configure_loggers
from TwitchChannelPointsMiner.classes.PubsubTopic import PubsubTopic
from TwitchChannelPointsMiner.classes.Streamer import Streamer
from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.TwitchBrowser import (
    BrowserSettings,
    TwitchBrowser,
)
from TwitchChannelPointsMiner.classes.WebSocketsPool import WebSocketsPool
from TwitchChannelPointsMiner.utils import get_user_agent

# Suppress warning for urllib3.connectionpool (selenium close connection)
# Suppress also the selenium logger please
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


class TwitchChannelPointsMiner:
    def __init__(
        self,
        username: str,
        make_predictions: bool = True,
        follow_raid: bool = True,
        watch_streak: bool = False,
        claim_drops_startup: bool = False,
        drops_events: bool = False,
        logger_settings: LoggerSettings = LoggerSettings(),
        browser_settings: BrowserSettings = BrowserSettings(),
        bet_settings: BetSettings = BetSettings(),
    ):
        self.username = username
        self.browser_settings = browser_settings
        self.bet_settings = bet_settings

        self.twitch = Twitch(
            self.username, get_user_agent(self.browser_settings.browser)
        )
        self.twitch_browser = None
        self.follow_raid = follow_raid
        self.watch_streak = watch_streak
        self.drops_events = drops_events
        self.claim_drops_startup = claim_drops_startup
        self.streamers = []
        self.events_predictions = {}
        self.minute_watcher_thread = None
        self.ws_pool = None

        self.make_predictions = make_predictions

        self.session_id = str(uuid.uuid4())
        self.running = False
        self.start_datetime = None
        self.original_streamers = []

        self.logger_settings = logger_settings
        self.logs_file = configure_loggers(self.username, self.logger_settings)

        signal.signal(signal.SIGINT, self.end)
        signal.signal(signal.SIGSEGV, self.end)
        signal.signal(signal.SIGTERM, self.end)

    def mine(self, streamers: list = [], followers=False):
        self.run(streamers, followers)

    def run(self, streamers: list = [], followers=False):
        if self.running:
            logger.error("You can't start multiple sessions of this instance!")
        else:
            logger.info(
                f"Start session: '{self.session_id}'", extra={"emoji": ":bomb:"}
            )
            self.running = True
            self.start_datetime = datetime.now()

            self.twitch.login()

            if self.claim_drops_startup is True:
                self.twitch.claim_all_drops_from_inventory()

            # Clear streamers array
            # Remove duplicate 3. Preserving Order: Use OrderedDict (askpython .com)
            streamers = [streamer_name.lower().strip() for streamer_name in streamers]
            streamers = list(OrderedDict.fromkeys(streamers))

            if followers is True:
                # Append at the end with lowest priority
                followers_array = self.twitch.get_followers()
                logger.info(
                    f"Loading {len(followers_array)} followers from your profile!",
                    extra={"emoji": ":clipboard:"},
                )
                streamers += [fw for fw in followers_array if fw not in streamers]

            logger.info(
                f"Loading data for {len(streamers)} streamers. Please wait...",
                extra={"emoji": ":nerd_face:"},
            )
            for streamer_username in streamers:
                time.sleep(random.uniform(0.3, 0.7))
                streamer_username.lower().strip()
                try:
                    channel_id = self.twitch.get_channel_id(streamer_username)
                    streamer = Streamer(
                        streamer_username,
                        channel_id,
                        less_printing=self.logger_settings.less,
                    )
                    self.streamers.append(streamer)
                except StreamerDoesNotExistException:
                    logger.info(
                        f"Streamer {streamer_username} does not exist",
                        extra={"emoji": ":cry:"},
                    )

            for streamer in self.streamers:
                time.sleep(random.uniform(0.3, 0.7))
                self.twitch.load_channel_points_context(
                    streamer, less_printing=self.logger_settings.less
                )
                self.twitch.check_streamer_online(streamer)
                self.twitch.viewer_is_mod(streamer)
            self.original_streamers = copy.deepcopy(self.streamers)

            if (
                self.make_predictions is True
            ):  # We need a browser to make predictions / bet
                self.twitch_browser = TwitchBrowser(
                    self.twitch.twitch_login.get_auth_token(),
                    self.session_id,
                    settings=self.browser_settings,
                )
                self.twitch_browser.init()

            self.minute_watcher_thread = threading.Thread(
                target=self.twitch.send_minute_watched_events,
                args=(
                    self.streamers,
                    self.watch_streak,
                ),
            )
            # self.minute_watcher_thread.daemon = True
            self.minute_watcher_thread.start()

            self.ws_pool = WebSocketsPool(
                twitch=self.twitch,
                twitch_browser=self.twitch_browser,
                streamers=self.streamers,
                bet_settings=self.bet_settings,
                events_predictions=self.events_predictions,
                less_printing=self.logger_settings.less,
            )
            topics = [
                PubsubTopic(
                    "community-points-user-v1",
                    user_id=self.twitch.twitch_login.get_user_id(),
                )
            ]

            if self.drops_events is True:
                topics.append(
                    PubsubTopic(
                        "user-drop-events",
                        user_id=self.twitch.twitch_login.get_user_id(),
                    ),
                )

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
                time.sleep(random.uniform(20, 60))
                # Do an external control for WebSocket. Check if the thread is running
                if self.ws_pool.ws.elapsed_last_ping() > 5:
                    logger.info(
                        "The last ping was sent more than 5 minutes ago. Reconnecting to the WebSocket..."
                    )
                    WebSocketsPool.handle_websocket_reconnection(self.ws_pool.ws)

    def end(self, signum, frame):
        logger.info("CTRL+C Detected! Please wait just a moments!")

        if self.twitch_browser is not None:
            self.twitch_browser.browser.quit()

        self.running = self.twitch.running = False
        self.ws_pool.end()

        self.minute_watcher_thread.join()

        self.__print_report()
        time.sleep(3.5)  # Do sleep for ending browser and threads

        sys.exit(0)

    def __print_report(self):
        print("\n")
        logger.info(
            f"Ending session: '{self.session_id}'", extra={"emoji": ":stop_sign:"}
        )
        if self.logs_file is not None:
            logger.info(
                f"Logs file: {self.logs_file}", extra={"emoji": ":page_facing_up:"}
            )
        logger.info(
            f"Duration {datetime.now() - self.start_datetime}",
            extra={"emoji": ":hourglass:"},
        )

        if self.make_predictions:
            print("")
            logger.info(f"{self.bet_settings}", extra={"emoji": ":bar_chart:"})
            for event_id in self.events_predictions:
                if self.events_predictions[event_id].bet_confirmed is True:
                    self.events_predictions[event_id].set_less_printing(False)
                    logger.info(
                        f"{self.events_predictions[event_id].print_recap()}",
                        extra={"emoji": ":bar_chart:"},
                    )
            print("")

        for streamer_index in range(0, len(self.streamers)):
            self.streamers[streamer_index].set_less_printing(False)
            logger.info(
                f"{self.streamers[streamer_index]}, Total Points Gained (after farming - before farming): {_millify(self.streamers[streamer_index].channel_points - self.original_streamers[streamer_index].channel_points)}",
                extra={"emoji": ":robot:"},
            )
            if self.streamers[streamer_index].history != {}:
                logger.info(
                    f"{self.streamers[streamer_index].print_history()}",
                    extra={"emoji": ":moneybag:"},
                )
