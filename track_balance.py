import json
import threading
import time
from random import randrange
import websocket  # pip install websocket-client
from claim_bonus import claim_channel_points_bonus
from twitch_data import *


# For documentation on Twitch PubSub API, see https://dev.twitch.tv/docs/pubsub


def listen_for_channel_points():
    ws = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv/v1",
                                on_message=on_message, on_open=on_open)
    ws.run_forever()


class PubsubTopic:
    def __init__(self, topic, channel_login=None):
        self.topic = topic
        self.channel_login = channel_login

    def is_user_topic(self):
        return self.channel_login is None

    def __str__(self):
        if self.is_user_topic():
            return f"{self.topic}.{get_user_id()}"
        else:
            return f"{self.topic}.{get_channel_id(self.channel_login)}"


def get_needed_topics():
    topics = [PubsubTopic("community-points-user-v1")]
    for streamer_login in get_streamer_logins():
        topics.append(PubsubTopic("video-playback-by-id", streamer_login))
    return topics


def on_open(ws):
    def run():
        ping(ws)

        all_topics = get_needed_topics()
        for topic in all_topics:
            listen_for_topic(ws, topic)

        while True:
            ping(ws)
            time.sleep(30)

    threading.Thread(target=run).start()


def on_message(ws, message):
    response = json.loads(message)

    if response["type"] == "MESSAGE":
        # print("Received message: ", response)
        data = response["data"]
        topic, topic_user = data["topic"].split(".")
        message = json.loads(data["message"])

        if topic == "community-points-user-v1":
            message_data = message["data"]

            if message["type"] == "points-earned":
                channel_id = message_data["channel_id"]
                if channel_id in get_streamer_ids():
                    new_balance = message_data["balance"]["balance"]
                    channel_login = get_login_by_channel_id(channel_id)
                    print(f"{new_balance} channel points for {channel_login}!")
            elif message["type"] == "claim-available":
                channel_id = message_data["claim"]["channel_id"]
                if channel_id in get_streamer_ids():
                    claim_id = message_data["claim"]["id"]
                    streamer_login = get_login_by_channel_id(channel_id)
                    claim_channel_points_bonus(streamer_login, claim_id)

        elif topic == "video-playback-by-id":
            channel_id = topic_user
            channel_login = get_login_by_channel_id(channel_id)
            if message["type"] == "stream-down":
                set_offline(channel_login)

    elif response["type"] == "RESPONSE" and len(response.get("error", "")) > 0:
        raise RuntimeError(f"Error while trying to listen for a topic: {response}")

    elif response["type"] == "RECONNECT":
        print("Reconnecting to Twitch PubSub server...")
        ws.close()
        time.sleep(30)
        listen_for_channel_points()


def listen_for_topic(ws, topic):
    data = {"topics": [str(topic)]}
    if topic.is_user_topic:
        data["auth_token"] = get_auth_token()

    nonce = create_nonce()
    send(ws, {"type": "LISTEN", "nonce": nonce, "data": data})


def ping(ws):
    send(ws, {"type": "PING"})


def send(ws, request):
    request_str = json.dumps(request, separators=(',', ':'))
    ws.send(request_str)


# https://en.wikipedia.org/wiki/Cryptographic_nonce
def create_nonce(length=30):
    nonce = ""
    for i in range(length):
        char_index = randrange(0, 10 + 26 + 26)
        if char_index < 10:
            char = chr(ord('0') + char_index)
        elif char_index < 10 + 26:
            char = chr(ord('a') + char_index - 10)
        else:
            char = chr(ord('A') + char_index - 26 - 10)
        nonce += char

    return nonce
