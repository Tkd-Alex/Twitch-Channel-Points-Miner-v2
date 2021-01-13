import logging
import threading
import time
import json
import emoji

from dateutil import parser

from TwitchChannelPointsMiner.classes.EventPrediction import EventPrediction
from TwitchChannelPointsMiner.classes.Raid import Raid
from TwitchChannelPointsMiner.classes.TwitchWebSocket import TwitchWebSocket

logger = logging.getLogger(__name__)


def get_streamer_index(streamers, channel_id):
    return next(i for i, x in enumerate(streamers) if x.channel_id == channel_id)


# You can't listen for more than 50 topics at once
class WebSocketsPool:
    def __init__(self, twitch, twitch_browser, streamers):
        self.ws = None
        self.twitch = twitch
        self.twitch_browser = twitch_browser
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
        self.ws.keep_running = True
        self.ws.is_closed = False
        self.ws.is_opened = False
        self.ws.topics = []
        self.ws.pending_topics = []

        self.ws.twitch = self.twitch
        self.ws.twitch_browser = self.twitch_browser
        self.ws.streamers = self.streamers
        self.ws.events_predictions = {}

        self.ws.last_message_time = 0
        self.ws.last_message_type = None

        self.thread_ws = threading.Thread(target=lambda: self.ws.run_forever())
        self.thread_ws.daemon = True
        self.thread_ws.start()

    def end(self):
        self.ws.keep_running = False
        self.ws.close()

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

        thread_ws = threading.Thread(target=run)
        thread_ws.daemon = True
        thread_ws.start()

    @staticmethod
    def handle_websocket_reconnection(ws):
        ws.is_closed = True
        if ws.keep_running:
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
        logger.debug(f"Received: {message.strip()}")
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
                    streamer_index = get_streamer_index(
                        ws.streamers, message_data["channel_id"]
                    )
                    earned = message_data["point_gain"]["total_points"]
                    ws.streamers[streamer_index].channel_points = message_data[
                        "balance"
                    ]["balance"]
                    logger.info(
                        emoji.emojize(f":rocket:  +{earned} → {ws.streamers[streamer_index]} - Reason: {message_data['point_gain']['reason_code']}.", use_aliases=True)
                    )
                elif message_type == "claim-available":
                    streamer_index = get_streamer_index(
                        ws.streamers, message_data["claim"]["channel_id"]
                    )
                    ws.twitch.claim_channel_points_bonus(
                        ws.streamers[streamer_index], message_data["claim"]["id"]
                    )

            elif topic == "video-playback-by-id":
                streamer_index = get_streamer_index(ws.streamers, topic_user)
                if message_type == "stream-down":
                    ws.streamers[streamer_index].set_offline()
                elif message_type == "viewcount":
                    ws.twitch.check_streamer_online(ws.streamers[streamer_index])
                # There is stream-up message type, but it's sent earlier than the API updates

            elif topic == "raid":
                streamer_index = get_streamer_index(ws.streamers, topic_user)
                if message_type == "raid_update_v2":
                    raid = Raid(message["raid"]["id"], message["raid"]["target_login"])
                    ws.twitch.update_raid(ws.streamers[streamer_index], raid)

            elif topic == "predictions-channel-v1":
                streamer_index = get_streamer_index(
                    ws.streamers, topic_user
                )  # message_data["event"]["channel_id"]

                event_id = message_data["event"]["id"]
                event_status = message_data["event"]["status"]

                current_timestamp = parser.parse(message_data["timestamp"])

                if event_id not in ws.events_predictions:
                    if event_status == "ACTIVE":
                        event = EventPrediction(
                            ws.streamers[streamer_index],
                            event_id,
                            message_data["event"]["title"],
                            parser.parse(message_data["event"]["created_at"]),
                            (
                                float(
                                    message_data["event"]["prediction_window_seconds"]
                                )
                                - 20
                            ),
                            event_status,
                            message_data["event"]["outcomes"],
                        )
                        if event.closing_bet_after(current_timestamp) > 0:
                            ws.events_predictions[event_id] = event
                            if ws.twitch_browser.currently_is_betting is False:
                                if ws.twitch_browser.start_bet(
                                    ws.events_predictions[event_id]
                                ):
                                    # complete_bet_thread = threading.Timer(event.closing_bet_after(current_timestamp), ws.twitch.make_predictions, (ws.events_predictions[event_id],))
                                    complete_bet_thread = threading.Timer(
                                        event.closing_bet_after(current_timestamp),
                                        ws.twitch_browser.complete_bet,
                                        (ws.events_predictions[event_id],),
                                    )
                                    complete_bet_thread.daemon = True
                                    complete_bet_thread.start()

                                    logger.info(
                                        emoji.emojize(f":alarm_clock:  Thread should start and place the bet after: {event.closing_bet_after(current_timestamp)}s for the event: {ws.events_predictions[event_id]}", use_aliases=True)
                                    )

                else:
                    ws.events_predictions[event_id].status = event_status
                    ws.events_predictions[event_id].bet.update_outcomes(
                        message_data["event"]["outcomes"]
                    )

            elif topic == "predictions-user-v1":
                if (
                    message_type == "prediction-result"
                    and message_data["event"]["result"]
                ):
                    event_id = message_data["event"]["id"]
                    if event_id in ws.events_predictions:
                        logger.info(
                            emoji.emojize(f":bar_chart:  {ws.events_predictions[event_id]} - Result: {message_data['event']['result']['type']}, Points won: {message_data['event']['result']['type'] if message_data['event']['result']['type'] else 0}", use_aliases=True)
                        )

        elif response["type"] == "RESPONSE" and len(response.get("error", "")) > 0:
            raise RuntimeError(f"Error while trying to listen for a topic: {response}")

        elif response["type"] == "RECONNECT":
            WebSocketsPool.handle_websocket_reconnection(ws)
