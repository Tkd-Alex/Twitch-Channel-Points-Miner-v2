import time

from datetime import datetime, timezone
from random import randrange


def get_streamer_index(streamers, channel_id):
    try:
        return next(
            i for i, x in enumerate(streamers) if str(x.channel_id) == str(channel_id)
        )
    except StopIteration:
        return -1


def server_time(message_data):
    return (
        datetime.fromtimestamp(message_data["server_time"], timezone.utc).isoformat() + "Z"
        if message_data is not None and "server_time" in message_data
        else datetime.fromtimestamp(time.time(), timezone.utc).isoformat() + "Z"
    )


def get_timestamp(message):
    message_data = message["data"] if "data" in message else None
    return (
        server_time(message)
        if message_data is None
        else (
            message_data["timestamp"]
            if "timestamp" in message_data
            else server_time(message_data)
        )
    )


def get_channel_id(message, topic_user):
    message_data = message["data"] if "data" in message else None
    return (
        topic_user
        if message_data is None
        else (
            message_data["prediction"]["channel_id"]
            if "prediction" in message_data
            else (
                message_data["claim"]["channel_id"]
                if "claim" in message_data
                else (
                    message_data["channel_id"]
                    if "channel_id" in message_data
                    else topic_user
                )
            )
        )
    )


def float_round(value):
    return round(float(value), 2)


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