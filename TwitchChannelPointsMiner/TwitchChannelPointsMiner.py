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

from TwitchChannelPointsMiner.classes.entities.PubsubTopic import PubsubTopic
from TwitchChannelPointsMiner.classes.entities.Streamer import (
    Streamer,
    StreamerSettings,
)
from TwitchChannelPointsMiner.classes.Exceptions import StreamerDoesNotExistException
from TwitchChannelPointsMiner.classes.Settings import Settings
from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.TwitchBrowser import BrowserSettings
from TwitchChannelPointsMiner.classes.WebSocketsPool import WebSocketsPool
from TwitchChannelPointsMiner.logger import LoggerSettings, configure_loggers
from TwitchChannelPointsMiner.utils import (
    _millify,
    at_least_one_value_in_settings_is,
    get_user_agent,
    set_default_settings,
)

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
        streamer_settings: StreamerSettings = StreamerSettings(),
    ):
        self.username = username

        # Set as globally config
        Settings.logger = logger_settings
        Settings.browser = browser_settings

        # Init as default all the missing values
        streamer_settings.default()
        streamer_settings.bet.default()
        Settings.streamer_settings = streamer_settings

        user_agent = get_user_agent(browser_settings.browser)
        self.twitch = Twitch(self.username, user_agent)

        self.twitch_browser = None
        self.claim_drops_startup = claim_drops_startup
        self.streamers = []
        self.events_predictions = {}
        self.minute_watcher_thread = None
        self.ws_pool = None

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

            streamers_name: list = []
            streamers_dict: dict = {}

            for streamer in streamers:
                username = (
                    streamer.username
                    if isinstance(streamer, Streamer)
                    else streamer.lower().strip()
                )
                streamers_name.append(username)
                streamers_dict[username] = streamer

            if followers is True:
                followers_array = self.twitch.get_followers()
                logger.info(
                    f"Load {len(followers_array)} followers from your profile!",
                    extra={"emoji": ":clipboard:"},
                )
                for username in followers_array:
                    if username not in streamers_dict:
                        streamers_dict[username] = username.lower().strip()
            else:
                followers_array = []

            streamers_name = list(
                OrderedDict.fromkeys(streamers_name + followers_array)
            )

            logger.info(
                f"Loading data for {len(streamers_name)} streamers. Please wait...",
                extra={"emoji": ":nerd_face:"},
            )
            for username in streamers_name:
                time.sleep(random.uniform(0.3, 0.7))
                try:

                    if isinstance(streamers_dict[username], Streamer) is True:
                        streamer = streamers_dict[username]
                    else:
                        streamer = Streamer(username)

                    streamer.channel_id = self.twitch.get_channel_id(username)
                    streamer.settings = set_default_settings(
                        streamer.settings, Settings.streamer_settings
                    )
                    streamer.settings.bet = set_default_settings(
                        streamer.settings.bet, Settings.streamer_settings.bet
                    )

                    self.streamers.append(streamer)
                except StreamerDoesNotExistException:
                    logger.info(
                        f"Streamer {username} does not exist",
                        extra={"emoji": ":cry:"},
                    )

            # Populate the streamers with default values.
            # 1. Load channel points and auto-claim bonus
            # 2. Check if streamers is online
            # 3. Check if the user is a Streamer. In thi case you can't do prediction
            for streamer in self.streamers:
                time.sleep(random.uniform(0.3, 0.7))
                self.twitch.load_channel_points_context(streamer)
                self.twitch.check_streamer_online(streamer)
                self.twitch.viewer_is_mod(streamer)
                if streamer.viewer_is_mod is True:
                    streamer.settings.make_predictions = False

            self.original_streamers = copy.deepcopy(self.streamers)

            # If we have at least one streamer with settings = make_predictions True
            make_predictions = at_least_one_value_in_settings_is(
                self.streamers, "make_predictions", True
            )

            self.minute_watcher_thread = threading.Thread(
                target=self.twitch.send_minute_watched_events,
                args=(
                    self.streamers,
                    at_least_one_value_in_settings_is(
                        self.streamers, "watch_streak", True
                    ),
                ),
            )
            self.minute_watcher_thread.start()

            self.ws_pool = WebSocketsPool(
                twitch=self.twitch,
                streamers=self.streamers,
                events_predictions=self.events_predictions,
            )

            # Subscribe to community-points-user. Get update for points spent or gains
            self.ws_pool.submit(
                PubsubTopic(
                    "community-points-user-v1",
                    user_id=self.twitch.twitch_login.get_user_id(),
                )
            )

            # If we have at least one streamer with settings = claim_drops True
            # Going to subscribe to user-drop-events. Get update for drop-progress
            claim_drops = at_least_one_value_in_settings_is(
                self.streamers, "claim_drops", True
            )
            if claim_drops is True:
                self.ws_pool.submit(
                    PubsubTopic(
                        "user-drop-events",
                        user_id=self.twitch.twitch_login.get_user_id(),
                    )
                )

            # Going to subscribe to predictions-user-v1. Get update when we place a new prediction (confirm)
            if make_predictions is True:
                self.ws_pool.submit(
                    PubsubTopic(
                        "predictions-user-v1",
                        user_id=self.twitch.twitch_login.get_user_id(),
                    )
                )

            for streamer in self.streamers:
                self.ws_pool.submit(
                    PubsubTopic("video-playback-by-id", streamer=streamer)
                )

                if streamer.settings.follow_raid is True:
                    self.ws_pool.submit(PubsubTopic("raid", streamer=streamer))

                if streamer.settings.make_predictions is True:
                    self.ws_pool.submit(
                        PubsubTopic("predictions-channel-v1", streamer=streamer)
                    )

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

        for event_id in self.events_predictions:
            if (
                self.events_predictions[event_id].bet_confirmed is True
                and self.events_predictions[event_id].streamer.settings.make_predictions
                is True
            ):
                logger.info(
                    f"{self.events_predictions[event_id].streamer.settings.bet}",
                    extra={"emoji": ":bar_chart:"},
                )
                logger.info(
                    f"{self.events_predictions[event_id].print_recap()}",
                    extra={"emoji": ":bar_chart:"},
                )
        print("")

        for streamer_index in range(0, len(self.streamers)):
            logger.info(
                f"{repr(self.streamers[streamer_index])}, Total Points Gained (after farming - before farming): {_millify(self.streamers[streamer_index].channel_points - self.original_streamers[streamer_index].channel_points)}",
                extra={"emoji": ":robot:"},
            )
            if self.streamers[streamer_index].history != {}:
                logger.info(
                    f"{self.streamers[streamer_index].print_history()}",
                    extra={"emoji": ":moneybag:"},
                )
