# -*- coding: utf-8 -*-

import logging
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings
from TwitchChannelPointsMiner.classes.TwitchBrowser import Browser, BrowserSettings

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    claim_drops_startup=False,                  # If you want to auto claim all drops from Twitch inventory on startup
    logger_settings=LoggerSettings(
        save=True,                              # If you want to save logs in file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info)
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big use logging.INFO
        emoji=True,                             # On Windows we have a problem to print emoji. Set to false if you have a problem
        less=False                              # If you think that the logs are too much verborse set this to True
    ),
    browser_settings=BrowserSettings(
        browser=Browser.FIREFOX,                # Choose if you want to use Chrome or Firefox as browser
        show=False,                             # Show the browser during bet else headless mode
        do_screenshot=False,                    # Do screenshot during the bet
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,                  # If you want to Bet / Make prediction
        follow_raid=True,                       # Follow raid to obtain more points
        claim_drops=True,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        watch_streak=True,                      # If a streamer go online change the priotiry of streamers array and catch the watch screak. Issue #11
        bet=BetSettings(
            strategy=Strategy.SMART,            # Choose you strategy!
            percentage=5,                       # Place the x% of your channel points
            percentage_gap=20,                  # Gap difference between outcomesA and outcomesB (for SMART stragegy)
            max_points=50000,                   # If the x percentage of your channel points is gt bet_max_points set this value
            stealth_mode=True,                  # If the calculated amount of channel points is GT the highest bet, place the highest value minus 1-2 points #33
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,    # Where apply the filter. Allowed [PERCENTAGE_USERS, ODDS_PERCENTAGE, ODDS, TOP_POINTS, TOTAL_USERS, TOTAL_POINTS]
                where=Condition.LTE,           # The key must be [GT, LT, GTE, LTE] than value
                value=800
            )
        )
    )
)

# You can customize the settings for each streamer. If not settings was provided the script will use the streamer_settings from TwitchChannelPointsMiner.
# If no streamer_settings provided in TwitchChannelPointsMiner the script will use default settings.
# The streamers array can be a String -> username or Streamer instance.

# The settings priority are: settings in mine function, settings in TwitchChannelPointsMiner instance, default settings.
# For example if in the mine function you don't provide any value for 'make_prediction' but you have set it on TwitchChannelPointsMiner instance the script will take the value from here.
# If you haven't set any value even in the instance the default one will be used

twitch_miner.mine(
    [
        Streamer("streamer-username01", settings=StreamerSettings(make_predictions=True  , follow_raid=False , claim_drops=True  , watch_streak=True , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=True,  percentage_gap=20 , max_points=234   , filter_condition=FilterCondition(key=OutcomeKeys.TOTAL_USERS,      condition=Condition.LTE, value=800, decision=False) ) )),
        Streamer("streamer-username02", settings=StreamerSettings(make_predictions=False , follow_raid=True  , claim_drops=False ,                     bet=BetSettings(strategy=Strategy.PERCENTAGE , percentage=5 , stealth_mode=False, percentage_gap=20 , max_points=1234  , filter_condition=FilterCondition(key=OutcomeKeys.TOTAL_POINTS,     condition=Condition.GTE, value=250, decision=False) ) )),
        Streamer("streamer-username03", settings=StreamerSettings(make_predictions=True  , follow_raid=False ,                     watch_streak=True , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=False, percentage_gap=30 , max_points=50000 , filter_condition=FilterCondition(key=OutcomeKeys.ODDS,             condition=Condition.LT, value=300, decision=True)   ) )),
        Streamer("streamer-username04", settings=StreamerSettings(make_predictions=False , follow_raid=True  ,                     watch_streak=True                                                                                                                                                                                                                                                     )),
        Streamer("streamer-username05", settings=StreamerSettings(make_predictions=True  , follow_raid=True  , claim_drops=True ,  watch_streak=True , bet=BetSettings(strategy=Strategy.HIGH_ODDS  , percentage=7 , stealth_mode=True,  percentage_gap=20 , max_points=90    , filter_condition=FilterCondition(key=OutcomeKeys.PERCENTAGE_USERS, condition=Condition.GTE, value=300, decision=True)  ) )),
        Streamer("streamer-username06"),
        Streamer("streamer-username07"),
        Streamer("streamer-username08"),
        "streamer-username09",
        "streamer-username10",
        "streamer-username11"
    ],                                 # Array of streamers (order = priority)
    followers=False                    # Automatic download the list of your followers (unable to set custom settings for you followers list)
)
