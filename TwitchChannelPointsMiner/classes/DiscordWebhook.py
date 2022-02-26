from textwrap import dedent

import requests

from TwitchChannelPointsMiner.classes.Settings import Events


class Discord(object):
    __slots__ = ["discord_webhook_api", "events"]

    def __init__(self, discord_webhook_api: str, events: list):
        self.discord_webhook_api = discord_webhook_api
        self.events = [str(e) for e in events]

    def send(self, message: str, event: Events) -> None:
        if str(event) in self.events:
            requests.post(
                url=self.discord_webhook_api,
                data={
                    "content": dedent(message),
                    "username": "Twitch Channel Points Miner",
                    "avatar_url": "https://i.imgur.com/X9fEkhT.png",
                },
            )
