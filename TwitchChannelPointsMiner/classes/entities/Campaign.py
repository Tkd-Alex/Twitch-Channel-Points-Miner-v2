from datetime import datetime

from TwitchChannelPointsMiner.classes.entities.Drop import Drop
from TwitchChannelPointsMiner.classes.Settings import Settings


class Campaign(object):
    __slots__ = [
        "id",
        "game",
        "name",
        "status",
        "in_inventory",
        "end_at",
        "start_at",
        "dt_match",
        "drops",
    ]

    def __init__(self, dict):
        self.id = dict["id"]
        self.game = dict["game"]
        self.name = dict["name"]
        self.status = dict["status"]
        self.in_inventory = False

        self.end_at = datetime.strptime(dict["endAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.start_at = datetime.strptime(dict["startAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.dt_match = self.start_at < datetime.now() < self.end_at

        self.drops = list(map(lambda x: Drop(x), dict["timeBasedDrops"]))

    def __repr__(self):
        return f"Campaign(id={self.id}, name={self.name}, game={self.game}, in_inventory={self.in_inventory})"

    def __str__(self):
        return (
            f"{self.name}, Game: {self.game['displayName']} - Drops: {len(self.drops)} pcs. - In inventory: {self.in_inventory}"
            if Settings.logger.less
            else self.__repr__()
        )

    def clear_drops(self):
        self.drops = list(
            filter(lambda x: x.dt_match is True and x.is_claimed is False, self.drops)
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False
