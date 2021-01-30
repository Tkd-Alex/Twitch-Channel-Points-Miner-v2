# -*- coding: utf-8 -*-

import logging
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings
from TwitchChannelPointsMiner.classes.TwitchBrowser import Browser, BrowserSettings

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    make_predictions=True,              # If you want to Bet / Make prediction | The browser will never start
    follow_raid=True,                   # Follow raid to obtain more points
    watch_streak=True,                  # If a streamer go online change the priotiry of streamers array and catch the watch screak. Issue #11
    drops_events=True,                  # If you want to auto claim game drops from Twitch inventory Issue #21
    claim_drops_startup=False,          # If you want to auto claim all drops from Twitch inventory on startup
    logger_settings=LoggerSettings(
        save=True,                      # If you want to save logs in file (suggested)
        console_level=logging.INFO,     # Level of logs - use logging.DEBUG for more info)
        file_level=logging.DEBUG,       # Level of logs - If you think the log file it's too big use logging.INFO
        emoji=True,                     # On Windows we have a problem to print emoji. Set to false if you have a problem
        less=False                      # If you think that the logs are too much verborse set this to True
    ),
    browser_settings=BrowserSettings(
        browser=Browser.FIREFOX,        # Choose if you want to use Chrome or Firefox as browser
        show=False,                     # Show the browser during bet else headless mode
        do_screenshot=False,            # Do screenshot during the bet
    ),
    bet_settings=BetSettings(
        strategy=Strategy.SMART,        # Choose you strategy!
        percentage=5,                   # Place the x% of your channel points
        percentage_gap=20,              # Gap difference between outcomesA and outcomesB (for SMART stragegy)
        max_points=50000,               # If the x percentage of your channel points is gt bet_max_points set this value
    )
)

twitch_miner.mine(
    ["streamer1", "streamer2"],         # Array of streamers (order = priority)
    followers=False                     # Automatic download the list of your followers
)
