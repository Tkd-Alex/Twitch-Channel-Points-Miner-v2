import platform
import re
import time
from datetime import datetime, timezone
from random import randrange
from millify import millify

from TwitchChannelPointsMiner.constants.browser import USER_AGENTS


def _millify(input, precision=2):
    return millify.millify(input, precision)


def get_streamer_index(streamers: list, channel_id) -> int:
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
def create_nonce(length=30) -> str:
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


def bet_condition(twitch_browser, event, logger) -> bool:
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
        logger.info(f"Sorry, you are moderator of {event.streamer}, so you can't bet!")
        return False
    return True


def get_user_agent(browser) -> str:
    try:
        return USER_AGENTS[platform.system()][
            browser.name if type(browser) != str else browser
        ]
    except KeyError:
        return USER_AGENTS["Linux"]["FIREFOX"]


def remove_emoji(string: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "\u231b"
        "\u2328"
        "\u23cf"
        "\u23e9"
        "\u23ea"
        "\u23eb"
        "\u23ec"
        "\u23ed"
        "\u23ee"
        "\u23ef"
        "\u23f0"
        "\u23f1"
        "\u23f2"
        "\u23f3"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", string)
