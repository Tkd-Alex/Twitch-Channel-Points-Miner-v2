import logging
import threading
import websocket  # pip install websocket-client
import time
import json

from TwitchChannelPointsMiner.classes.Raid import Raid
from TwitchChannelPointsMiner.classes.TwitchWebSocket import TwitchWebSocket

logger = logging.getLogger(__name__)

# You can't listen for more than 50 topics at once
class WebSocketsPool:
    def __init__(self, twitch, streamers):
        self.ws = None
        self.twitch = twitch
        self.streamers = streamers

    def submit(self, topic):
        if self.ws is None or len(self.ws.topics) >= 50:
            self.create_new_websocket()

        self.ws.topics.append(topic)

        if not self.ws.is_opened:
            self.ws.pending_topics.append(topic)
        else:
            self.ws.listen(topic, self.twitch.twitch_login.get_auth_token())

    def create_new_websocket(self):
        self.ws = TwitchWebSocket(
            "wss://pubsub-edge.twitch.tv/v1",
            on_message=WebSocketsPool.on_message,
            on_open=WebSocketsPool.on_open,
            on_close=WebSocketsPool.handle_websocket_reconnection,
        )
        self.ws.parent_pool = self
        self.ws.is_closed = False
        self.ws.is_opened = False
        self.ws.topics = []
        self.ws.pending_topics = []

        self.ws.twitch = self.twitch
        self.ws.streamers = self.streamers

        self.ws.last_message_time = 0
        self.ws.last_message_type = None

        threading.Thread(target=lambda: self.ws.run_forever()).start()

    @staticmethod
    def on_open(ws):
        def run():
            ws.is_opened = True
            ws.ping()
            for topic in ws.pending_topics:
                ws.listen(topic, ws.twitch.twitch_login.get_auth_token())

            while not ws.is_closed:
                ws.ping()
                time.sleep(30)

        threading.Thread(target=run).start()

    @staticmethod
    def handle_websocket_reconnection(ws):
        ws.is_closed = True
        logger.info("Reconnecting to Twitch PubSub server in 30 seconds")
        time.sleep(30)
        self = ws.parent_pool
        if self.ws == ws:
            self.ws = None
        for topic in ws.topics:
            self.submit(topic)

    @staticmethod
    def on_message(ws, message):
        logger.info(f"Received: {message.strip()}")
        response = json.loads(message)

        if response["type"] == "MESSAGE":
            data = response["data"]
            topic, topic_user = data["topic"].split(".")

            message = json.loads(data["message"])
            message_type = message["type"]

            message_data = None
            if "data" in message:
                message_data = message["data"]

            # If we have more than one PubSub connection, messages may be duplicated
            if (
                time.time() - ws.last_message_time < 0.1
                and ws.last_message_type == message_type
            ):
                ws.last_message_time = time.time()
                return

            ws.last_message_time = time.time()
            ws.last_message_type = message_type

            if topic == "community-points-user-v1":
                if message_type == "points-earned":
                    channel_id = message_data["channel_id"]
                    streamer_index = next(
                        i
                        for i, x in enumerate(ws.streamers)
                        if x.channel_id == channel_id
                    )
                    streamer = ws.streamers[streamer_index]

                    new_balance = message_data["balance"]["balance"]
                    logger.info(
                        f"{new_balance} channel points for {streamer}! Reason: {message_data['point_gain']['reason_code']}."
                    )
                elif message_type == "claim-available":
                    channel_id = message_data["claim"]["channel_id"]
                    streamer_index = next(
                        i
                        for i, x in enumerate(ws.streamers)
                        if x.channel_id == channel_id
                    )
                    streamer = ws.streamers[streamer_index]

                    ws.twitch.claim_channel_points_bonus(
                        streamer.username, message_data["claim"]["id"]
                    )

            elif topic == "video-playback-by-id":
                streamer_index = next(
                    i for i, x in enumerate(ws.streamers) if x.channel_id == topic_user
                )
                if message_type == "stream-down":
                    ws.streamers[streamer_index].set_offline()
                elif message_type == "viewcount":
                    ws.twitch.check_streamer_online(ws.streamers[streamer_index])
                # There is stream-up message type, but it's sent earlier than the API updates

            elif topic == "raid":
                streamer_index = next(
                    i for i, x in enumerate(ws.streamers) if x.channel_id == topic_user
                )
                if message_type == "raid_update_v2":
                    raid = Raid(message["raid"]["id"], message["raid"]["target_login"])
                    ws.twitch.update_raid(ws.streamers[streamer_index], raid)

        elif response["type"] == "RESPONSE" and len(response.get("error", "")) > 0:
            raise RuntimeError(f"Error while trying to listen for a topic: {response}")

        elif response["type"] == "RECONNECT":
            WebSocketsPool.handle_websocket_reconnection(ws)
