import json
import requests
from claim_bonus import post_gql_request
from twitch_data import get_auth_token


class Raid:
    def __init__(self, raid_id, target_login):
        self.raid_id = raid_id
        self.target_login = target_login


raid_id_for_streamer = {}


def set_raid(streamer_login, raid):
    if raid_id_for_streamer.get(streamer_login) != raid:
        raid_id_for_streamer[streamer_login] = raid
        r = post_gql_request(
            {"operationName": "JoinRaid",
             "variables": {"input": {"raidID": raid.raid_id}},
             "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "c6a332a86d1087fbbb1a8623aa01bd1313d2386e7c63be60fdb2d1901f01a4ae"}}})

        print(f"Joining raid from {streamer_login} to {raid.target_login}! Response: {r.text}")


def follow_raid(streamer_login):
    raid = raid_id_for_streamer[streamer_login]
    raid_id_for_streamer[streamer_login] = None  # don't follow a raid twice

    access_token = get_access_token(raid.target_login)
    token = bytes(access_token["token"], "utf-8").decode("unicode_escape")
    sig = access_token["sig"]

    requests.get(f"https://usher.ttvnw.net/api/channel/hls/{streamer_login}.m3u8",
                 params={"sig": sig, "token": token, "raid_id": raid.raid_id, "fast_bread": "true"})
    print(f"Followed raid from {streamer_login} to {raid.target_login}!")


def get_access_token(streamer_login):
    url = f"https://api.twitch.tv/api/channels/{streamer_login}/access_token?need_https=true" \
          f"&oauth_token={get_auth_token()}&platform=web&player_backend=mediaplayer&player_type=site"
    r = requests.get(url)
    return r.json()