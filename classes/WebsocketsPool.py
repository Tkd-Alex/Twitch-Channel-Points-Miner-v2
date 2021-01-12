import logging
import threading
import websocket
import time

logger = logging.getLogger(__name__)

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
            on_message=on_message,
            on_open=WebsocketsPool.on_open,
            on_close=WebsocketsPool.handle_websocket_reconnection
        )
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
        logger.info("Reconnecting to Twitch PubSub server in 30 seconds")
        time.sleep(30)
        self = ws.parent_pool
        if self.free_websocket == ws:
            self.free_websocket = None
        for topic in ws.topics:
            self.submit(topic)
