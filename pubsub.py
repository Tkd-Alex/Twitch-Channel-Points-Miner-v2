import json
import threading
import time
from random import randrange
import websocket  # pip install websocket-client
from claim_bonus import claim_channel_points_bonus
from raid import update_raid, Raid
from twitch_data import *


# For documentation on Twitch PubSub API, see https://dev.twitch.tv/docs/pubsub


def listen_for_channel_points():
    ws_pool = WebsocketsPool()
    for topic in get_needed_topics():
        ws_pool.submit(topic)


def get_needed_topics():
    topics = [PubsubTopic("community-points-user-v1")]
    for streamer_login in get_streamer_logins():
        topics.append(PubsubTopic("video-playback-by-id", streamer_login))
        topics.append(PubsubTopic("raid", streamer_login))
    return topics


def on_open(ws):
    def run():
        ping(ws)

        all_topics = get_needed_topics()
        for topic in all_topics:
            listen_for_topic(ws, topic)

        while not ws.is_closed:
            ping(ws)
            time.sleep(30)

    threading.Thread(target=run).start()


last_message_time = 0
last_message_type = None


def on_message(ws, message):
    global last_message_time, last_message_type
    response = json.loads(message)

    if response["type"] == "MESSAGE":
        # print("Received message: ", response)
        data = response["data"]
        topic, topic_user = data["topic"].split(".")
        message = json.loads(data["message"])
        message_type = message["type"]
        message_data = None
        if "data" in message:
            message_data = message["data"]

        # If we have more than one PubSub connection, messages may be duplicated
        if time.time() - last_message_time < 0.1 and last_message_type == message_type:
            last_message_time = time.time()
            return
        last_message_time = time.time()
        last_message_type = message_type

        if topic == "community-points-user-v1":
            if message_type == "points-earned":
                channel_id = message_data["channel_id"]
                if channel_id in get_streamer_ids():
                    new_balance = message_data["balance"]["balance"]
                    channel_login = get_login_by_channel_id(channel_id)
                    reason_name = get_reason_name(message_data["point_gain"]["reason_code"])
                    print(f"{new_balance} channel points for {channel_login}! Reason: {reason_name}.")
            elif message_type == "claim-available":
                channel_id = message_data["claim"]["channel_id"]
                if channel_id in get_streamer_ids():
                    claim_id = message_data["claim"]["id"]
                    streamer_login = get_login_by_channel_id(channel_id)
                    claim_channel_points_bonus(streamer_login, claim_id)

        elif topic == "video-playback-by-id":
            channel_login = get_login_by_channel_id(topic_user)
            if message_type == "stream-down":
                set_offline(channel_login)
            elif message_type == "viewcount":
                check_online(channel_login)
            # there is stream-up message type, but it's sent earlier than the API updates

        elif topic == "raid":
            channel_login = get_login_by_channel_id(topic_user)
            if message_type == "raid_update_v2":
                # streamer_login is going to raid someone
                raid_info = message["raid"]
                raid = Raid(raid_info["id"], raid_info["target_login"])
                update_raid(channel_login, raid)

    elif response["type"] == "RESPONSE" and len(response.get("error", "")) > 0:
        raise RuntimeError(f"Error while trying to listen for a topic: {response}")

    elif response["type"] == "RECONNECT":
        WebsocketsPool.handle_websocket_reconnection(ws)


def get_reason_name(code):
    return code.replace("_", " ").replace("CLAIM", "bonus claimed").lower()


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


class WebsocketsPool:  # you can't listen for more than 50 topics at once
    def __init__(self):
        self.free_websocket = None

    def submit(self, pubsub_topic):
        if self.free_websocket is None or len(self.free_websocket.topics) >= 50:
            self.create_new_websocket()
        self.free_websocket.topics.append(pubsub_topic)
        if not self.free_websocket.is_opened:
            self.free_websocket.pending_topics.append(pubsub_topic)
        else:
            listen_for_topic(self.free_websocket, pubsub_topic)

    def create_new_websocket(self):
        self.free_websocket = websocket.WebSocketApp("wss://pubsub-edge.twitch.tv/v1",
            on_message=on_message, on_open=WebsocketsPool.on_open, on_close=WebsocketsPool.handle_websocket_reconnection)
        self.free_websocket.parent_pool = self
        self.free_websocket.is_closed = False
        self.free_websocket.is_opened = False
        self.free_websocket.topics = []
        self.free_websocket.pending_topics = []
        threading.Thread(target=lambda: self.free_websocket.run_forever()).start()

    @staticmethod
    def on_open(ws):
        def run():
            ws.is_opened = True
            ping(ws)
            for topic in ws.pending_topics:
                listen_for_topic(ws, topic)
            while not ws.is_closed:
                ping(ws)
                time.sleep(30)

        threading.Thread(target=run).start()

    @staticmethod
    def handle_websocket_reconnection(ws):
        ws.is_closed = True
        print("Reconnecting to Twitch PubSub server in 30 seconds")
        time.sleep(30)
        self = ws.parent_pool
        if self.free_websocket == ws:
            self.free_websocket = None
        for topic in ws.topics:
            self.submit(topic)


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
