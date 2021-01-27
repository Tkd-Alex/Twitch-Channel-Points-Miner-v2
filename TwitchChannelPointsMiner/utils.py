import time
import platform

from datetime import datetime, timezone
from random import randrange

from TwitchChannelPointsMiner.constants import USER_AGENTS


def get_streamer_index(streamers, channel_id):
    try:
        return next(
            i for i, x in enumerate(streamers) if str(x.channel_id) == str(channel_id)
        )
    except StopIteration:
        return -1


def float_round(number, ndigits=2):
    return round(float(number), ndigits)


def server_time(message_data):
    return (
        datetime.fromtimestamp(message_data["server_time"], timezone.utc).isoformat()
        + "Z"
        if message_data is not None and "server_time" in message_data
        else datetime.fromtimestamp(time.time(), timezone.utc).isoformat() + "Z"
    )


def calculate_start_after(closing_bet_after, execution_time):
    return round(max(1, closing_bet_after - execution_time), 2)


# https://en.wikipedia.org/wiki/Cryptographic_nonce
def create_nonce(length=30):
    nonce = ""
    for i in range(length):
        char_index = randrange(0, 10 + 26 + 26)
        if char_index < 10:
            char = chr(ord("0") + char_index)
        elif char_index < 10 + 26:
            char = chr(ord("a") + char_index - 10)
        else:
            char = chr(ord("A") + char_index - 26 - 10)
        nonce += char
    return nonce


def bet_condition(twitch_browser, event, logger):
    if twitch_browser.currently_is_betting is True:
        logger.info(
            f"Sorry, unable to start {event}, the browser is currently betting on another event!"
        )
        return False
    elif twitch_browser.browser.current_url != "about:blank":
        logger.info(
            "Sorry, but the browser is not currently on 'about:blank' screen. Unable to start bet!"
        )
        return False
    elif event.streamer.viewer_is_mod is True:
        logger.info(
            f"Sorry, you are moderator of {event.streamer}, so you can't bet!"
        )
        return False
    return True


def get_user_agent(browser):
    try:
        return USER_AGENTS[platform.system()][browser.name if type(browser) != str else browser]
    except KeyError:
        return USER_AGENTS["Linux"]["FIREFOX"]
