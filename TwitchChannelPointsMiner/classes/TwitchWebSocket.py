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
        self.last_ping = time.time()

    def send(self, request):
        request_str = json.dumps(request, separators=(",", ":"))
        logger.debug(f"Send: {request_str}")
        super().send(request_str)

    def reset(self, parent_pool):
        self.parent_pool = parent_pool
        self.keep_running = True
        self.is_closed = False
        self.is_opened = False

        # Custom attribute
        self.topics = []
        self.pending_topics = []

        self.twitch = parent_pool.twitch
        self.twitch_browser = parent_pool.twitch_browser
        self.streamers = parent_pool.streamers
        self.bet_settings = parent_pool.bet_settings
        self.events_predictions = parent_pool.events_predictions
        self.less_printing = parent_pool.less_printing

        self.last_message_time = 0
        self.last_message_type_topic = None

        self.last_pong = time.time()
        self.last_ping = time.time()

    def elapsed_last_pong(self):
        return (time.time() - self.last_pong) // 60

    def elapsed_last_ping(self):
        return (time.time() - self.last_ping) // 60
