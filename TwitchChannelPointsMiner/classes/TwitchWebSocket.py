import json
import logging
import time

from random import randrange
from websocket import WebSocketApp

logger = logging.getLogger(__name__)


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


class TwitchWebSocket(WebSocketApp):
    def listen(self, topic, auth_token=None):
        data = {"topics": [str(topic)]}
        if topic.is_user_topic() and auth_token is not None:
            data["auth_token"] = auth_token

        nonce = create_nonce()
        self.send({"type": "LISTEN", "nonce": nonce, "data": data})

    def ping(self):
        self.send({"type": "PING"})

    def send(self, request):
        request_str = json.dumps(request, separators=(",", ":"))
        logger.debug(f"Send: {request_str}")
        super().send(request_str)

    def reset(self, parent_pool):
        self.ws.parent_pool = parent_pool
        self.ws.keep_running = True
        self.ws.is_closed = False
        self.ws.is_opened = False

        # Custom attribute
        self.ws.topics = []
        self.ws.pending_topics = []

        self.ws.twitch = parent_pool.twitch
        self.ws.twitch_browser = parent_pool.twitch_browser
        self.ws.streamers = parent_pool.streamers
        self.ws.bet_settings = parent_pool.bet_settings
        self.ws.events_predictions = parent_pool.events_predictions

        self.ws.last_message_time = 0
        self.ws.last_message_type = None
        self.ws.last_pong = time.time()
