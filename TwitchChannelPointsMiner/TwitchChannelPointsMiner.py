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

from TwitchChannelPointsMiner.classes.entities.Bet import BetSettings
from TwitchChannelPointsMiner.classes.entities.PubsubTopic import PubsubTopic
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer
from TwitchChannelPointsMiner.classes.Exceptions import StreamerDoesNotExistException
from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.TwitchBrowser import (
    BrowserSettings,
    TwitchBrowser,
)
from TwitchChannelPointsMiner.classes.WebSocketsPool import WebSocketsPool
from TwitchChannelPointsMiner.logger import LoggerSettings, configure_loggers
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
        claim_drops_startup: bool = False,
        # Settings for logging and selenium as you can see.
        # This settings will be global shared trought Settings class
        logger_settings: LoggerSettings = LoggerSettings(),
        browser_settings: BrowserSettings = BrowserSettings(),
        # Default values for all streamers
        bet_settings: BetSettings = BetSettings(),
        make_predictions: bool = True,
        follow_raid: bool = True,
        watch_streak: bool = False,
        drops_events: bool = False,
    ):
        self.username = username

        # Set as globally config
        Settings.logger = logger_settings
        Settings.browser = browser_settings
        Settings.bet = bet_settings

        user_agent = get_user_agent(browser_settings.browser)
        self.twitch = Twitch(self.username, user_agent)

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

        self.logs_file = configure_loggers(self.username, logger_settings)

        for sign in [signal.SIGINT, signal.SIGSEGV, signal.SIGTERM]:
            signal.signal(sign, self.end)

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
                    f"Load {len(followers_array)} followers from your profile!",
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
                    streamer = Streamer(streamer_username, channel_id)
                    self.streamers.append(streamer)
                except StreamerDoesNotExistException:
                    logger.info(
                        f"Streamer {streamer_username} does not exist",
                        extra={"emoji": ":cry:"},
                    )

            for streamer in self.streamers:
                time.sleep(random.uniform(0.3, 0.7))
                self.twitch.load_channel_points_context(streamer)
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
                events_predictions=self.events_predictions,
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
            # logger.info(f"{self.bet_settings}", extra={"emoji": ":bar_chart:"})
            for event_id in self.events_predictions:
                if self.events_predictions[event_id].bet_confirmed is True:
                    logger.info(
                        f"{self.events_predictions[event_id].print_recap()}",
                        extra={"emoji": ":bar_chart:"},
                    )
            print("")

        for streamer_index in range(0, len(self.streamers)):
            logger.info(
                f"{self.streamers[streamer_index]}, Total Points Gained (after farming - before farming): {self.streamers[streamer_index].channel_points - self.original_streamers[streamer_index].channel_points}",
                extra={"emoji": ":robot:"},
            )
            if self.streamers[streamer_index].history != {}:
                logger.info(
                    f"{self.streamers[streamer_index].print_history()}",
                    extra={"emoji": ":moneybag:"},
                )
