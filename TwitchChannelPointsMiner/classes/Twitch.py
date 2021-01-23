# For documentation on Twitch GraphQL API see:
# https://www.apollographql.com/docs/
# https://github.com/mauricew/twitch-graphql-api
# Full list of available methods: https://azr.ivr.fi/schema/query.doc.html (a bit outdated)


import requests
import json
import re
import os
import time
import logging
import random

from base64 import b64encode
from pathlib import Path

from TwitchChannelPointsMiner.classes.RequestInfo import RequestInfo
from TwitchChannelPointsMiner.classes.TwitchLogin import TwitchLogin
from TwitchChannelPointsMiner.classes.Exceptions import (
    StreamerIsOfflineException,
    StreamerDoesNotExistException,
)

TWITCH_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

logger = logging.getLogger(__name__)


class Twitch:
    def __init__(self, username):
        cookies_path = os.path.join(Path().absolute(), "cookies")
        Path(cookies_path).mkdir(parents=True, exist_ok=True)
        self.cookies_file = os.path.join(cookies_path, f"{username}.pkl")
        self.twitch_login = TwitchLogin(TWITCH_CLIENT_ID, username, USER_AGENT)
        self.running = True

    def login(self):
        if os.path.isfile(self.cookies_file) is False:
            if self.twitch_login.login_flow():
                self.twitch_login.save_cookies(self.cookies_file)
        else:
            self.twitch_login.load_cookies(self.cookies_file)
            self.twitch_login.set_token(self.twitch_login.get_auth_token())

    def update_minute_watched_event_request(self, streamer):
        event_properties = {
            "channel_id": streamer.channel_id,
            "broadcast_id": self.get_broadcast_id(streamer),
            "player": "site",
            "user_id": self.twitch_login.get_user_id(),
        }
        minute_watched = [{"event": "minute-watched", "properties": event_properties}]
        json_event = json.dumps(minute_watched, separators=(",", ":"))
        streamer.minute_watched_requests = RequestInfo(
            self.get_minute_watched_request_url(streamer),
            {"data": (b64encode(json_event.encode("utf-8"))).decode("utf-8")},
        )

    def get_minute_watched_request_url(self, streamer):
        main_page_request = requests.get(
            streamer.streamer_url, headers={"User-Agent": USER_AGENT}
        )
        response = main_page_request.text
        settings_url = re.search(
            "(https://static.twitchcdn.net/config/settings.*?js)", response
        ).group(1)

        settings_request = requests.get(
            settings_url, headers={"User-Agent": USER_AGENT}
        )
        response = settings_request.text
        minute_watched_request_url = re.search('"spade_url":"(.*?)"', response).group(1)
        return minute_watched_request_url

    def post_gql_request(self, json_data):
        response = requests.post(
            "https://gql.twitch.tv/gql",
            json=json_data,
            headers={
                "Authorization": f"OAuth {self.twitch_login.get_auth_token()}",
                "Client-Id": TWITCH_CLIENT_ID,
                "User-Agent": USER_AGENT,
            },
        )
        logger.debug(
            f"Data: {json_data}, Status code: {response.status_code}, Content: {response.json()}"
        )
        return response.json()

    def get_broadcast_id(self, streamer):
        json_data = {
            "operationName": "WithIsStreamLiveQuery",
            "variables": {"id": streamer.channel_id},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "04e46329a6786ff3a81c01c50bfa5d725902507a0deb83b0edbf7abe7a3716ea",
                }
            },
        }
        response = self.post_gql_request(json_data)
        stream = response["data"]["user"]["stream"]
        if stream is not None:
            return stream["id"]
        else:
            raise StreamerIsOfflineException

    def check_streamer_online(self, streamer):
        if time.time() < streamer.offline_at + 60:
            return

        if streamer.is_online is False:
            try:
                self.update_minute_watched_event_request(streamer)
            except StreamerIsOfflineException:
                streamer.set_offline()
            else:
                streamer.set_online()

    def claim_bonus(self, streamer, claim_id):
        logger.info(f"Claiming the bonus for {streamer}!", extra={"emoji": ":gift:"})
        json_data = {
            "operationName": "ClaimCommunityPoints",
            "variables": {
                "input": {"channelID": streamer.channel_id, "claimID": claim_id}
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "46aaeebe02c99afdf4fc97c7c0cba964124bf6b0af229395f1f6d1feed05b3d0",
                }
            },
        }
        self.post_gql_request(json_data)

    # Load the amount of current points for a channel, check if a bonus is available
    def load_channel_points_context(self, streamer):
        json_data = {
            "operationName": "ChannelPointsContext",
            "variables": {"channelLogin": streamer.username},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "9988086babc615a918a1e9a722ff41d98847acac822645209ac7379eecb27152",
                }
            },
        }
        response = self.post_gql_request(json_data)
        if response["data"]["community"] is None:
            raise StreamerDoesNotExistException
        community_points = response["data"]["community"]["channel"]["self"][
            "communityPoints"
        ]
        streamer.channel_points = community_points["balance"]
        # logger.info(f"{streamer.channel_points} channel points for {streamer.username}!")
        if community_points["availableClaim"] is not None:
            self.claim_bonus(streamer, community_points["availableClaim"]["id"])

    def make_predictions(self, event):
        decision = event.bet.calculate(event.streamer.channel_points)
        return self.post_gql_request(
            {
                "operationName": "MakePrediction",
                "variables": {
                    "input": {
                        "eventID": event.event_id,
                        "outcomeID": decision["id"],
                        "points": decision["amount"],
                        "transactionID": "412118d3********79ac856",  # How we can calculate this?
                    }
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "b44682ecc88358817009f20e69d75081b1e58825bb40aa53d5dbadcc17c881d8",
                    }
                },
            }
        )

    def send_minute_watched_events(self, streamers, watch_streak=False):
        headers = {"user-agent": USER_AGENT}
        while self.running:
            # Twitch has a limit - you can't watch more than 2 channels at one time.
            # We take the first two streamers from the list as they have the highest priority.
            streamers_index = [
                i for i in range(0, len(streamers)) if streamers[i].is_online
            ]

            # Check if we need need to change priority based on watch streak
            """
            Viewers receive points for returning for x consecutive streams.
            Each stream must be at least 10 minutes long and it must have been at least 30 minutes since the last stream ended.
            """
            streamers_watching = []
            if watch_streak is True:
                for index in streamers_index:
                    if (
                        streamers[index].watch_streak_missing is True
                        and (
                            streamers[index].offline_at == 0
                            or ((time.time() - streamers[index].offline_at) // 60) > 30
                        )
                        and streamers[index].minute_watched <= random.uniform(16, 18)
                    ):
                        logger.info(
                            f"Switch priority: {streamers[index]}, WatchStreak missing is {streamers[index].watch_streak_missing} and minute_watched: {streamers[index].minute_watched}"
                        )
                        streamers_watching.append(index)
                        if len(streamers_watching) == 2:
                            break

            if streamers_watching == []:
                streamers_watching = streamers_index
            else:
                while len(streamers_watching) < 2 and len(streamers_index) > 1:
                    another_streamer_index = streamers_index.pop(0)
                    if another_streamer_index not in streamers_watching:
                        streamers_watching.append(another_streamer_index)

            streamers_watching = streamers_watching[:2]
            for index in streamers_watching:
                next_iteration = time.time() + 60 / len(streamers_watching)
                try:
                    response = requests.post(
                        streamers[index].minute_watched_requests.url,
                        data=streamers[index].minute_watched_requests.payload,
                        headers=headers,
                    )
                    logger.debug(
                        f"Send minute watched request for {streamers[index]} - Status code: {response.status_code}"
                    )
                    if response.status_code == 204:
                        streamers[index].update_minute_watched()
                except requests.exceptions.ConnectionError as e:
                    logger.error(f"Error while trying to watch a minute: {e}")

                # Create chunk of sleep of speed-up the break loop after CTRL+C
                sleep_time = max(next_iteration - time.time(), 0) / 3
                for i in range(0, 3):
                    time.sleep(sleep_time)
                    if self.running is False:
                        break

            if not streamers_watching:
                time.sleep(60)

    def get_channel_id(self, streamer_username):
        json_response = self.__do_helix_request(f"/users?login={streamer_username}")
        data = json_response["data"]
        if len(data) >= 1:
            return data[0]["id"]
        else:
            raise StreamerDoesNotExistException

    def get_followers(self, first=100):
        followers = []
        pagination = {}
        while 1:
            query = f"/users/follows?from_id={self.twitch_login.get_user_id()}&first={first}"
            if pagination != {}:
                query += f"&after={pagination['cursor']}"

            json_response = self.__do_helix_request(query)
            pagination = json_response["pagination"]
            followers += [fw["to_name"].lower() for fw in json_response["data"]]
            time.sleep(random.uniform(0.3, 0.7))

            if pagination == {}:
                break

        return followers

    def __do_helix_request(self, query, response_as_json=True):
        url = f"https://api.twitch.tv/helix/{query.strip('/')}"
        response = self.twitch_login.session.get(url)
        logger.debug(
            f"Query: {query}, Status code: {response.status_code}, Content: {response.json()}"
        )
        return response.json() if response_as_json is True else response

    def update_raid(self, streamer, raid):
        if streamer.raid != raid:
            streamer.raid = raid
            self.post_gql_request(
                {
                    "operationName": "JoinRaid",
                    "variables": {"input": {"raidID": raid.raid_id}},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "c6a332a86d1087fbbb1a8623aa01bd1313d2386e7c63be60fdb2d1901f01a4ae",
                        }
                    },
                }
            )

            logger.info(
                f"Joining raid from {streamer} to {raid.target_login}!",
                extra={"emoji": ":performing_arts:"},
            )
