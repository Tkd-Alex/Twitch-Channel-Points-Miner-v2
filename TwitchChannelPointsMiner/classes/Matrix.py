from textwrap import dedent

import requests
from urllib.parse import quote

from TwitchChannelPointsMiner.classes.Settings import Events


class Matrix(object):
    __slots__ = ["access_token", "homeserver", "room_id", "events"]

    def __init__(self, username: str, password: str, homeserver: str, room_id: str):
        self.homeserver = homeserver
        self.room_id = quote(room_id)

        body = requests.post(
            url=f"https://{self.homeserver}/_matrix/client/r0/login",
            json={
                "user": username,
                "password": password,
                "type": "m.login.password"
            }
        ).json()

        self.access_token = body.get("access_token")

        if not self.access_token:
            print("[Matrix]: Invalid password provided. Notifications will not be sent.")

    def send(self, message: str, event: Events) -> None:
        if not self.access_token:
            return

        if str(event) in self.events:
            requests.post(
                url=f"https://{self.homeserver}/_matrix/client/r0/rooms/{self.room_id}/send/m.room.message?access_token={self.access_token}",
                json={
                    "body": message,
                    "msgtype": "m.text"
                }
            )
