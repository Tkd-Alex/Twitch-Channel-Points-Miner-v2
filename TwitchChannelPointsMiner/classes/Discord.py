from textwrap import dedent

import requests

from TwitchChannelPointsMiner.classes.Settings import Events


class Discord(object):
    __slots__ = ["webhook_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]

    def send(self, message: str, event: Events) -> None:
        if str(event) in self.events:
            requests.post(
                url=self.webhook_api,
                data={
                    "content": dedent(message),
                    "username": "⛏️ Twitch Miner",
                    "avatar_url": "https://img.icons8.com/external-smashingstocks-circular-smashing-stocks/260/000000/external-miner-bitcoin-blockchain-and-cryptocurrency-smashingstocks-circular-smashing-stocks.png",
                },
            )
