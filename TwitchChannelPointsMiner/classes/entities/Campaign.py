from datetime import datetime

from TwitchChannelPointsMiner.classes.entities.Drop import Drop


class Campaign(object):
    def __init__(self, dict):
        self.id = dict["id"]
        self.game = dict["game"]
        self.name = dict["name"]
        self.status = dict["status"]
        self.in_inventory = False

        self.end_at = datetime.strptime(dict["endAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.start_at = datetime.strptime(dict["startAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.dt_match = self.start_at < datetime.now() < self.end_at

        self.drops = [Drop(drop) for drop in dict["timeBasedDrops"]]

    def __repr__(self):
        return f"Campaign(id={self.id}, name={self.name}, game={self.game}, in_inventory={self.in_inventory})"

    def clear_drops(self):
        self.drops = [
            drop
            for drop in self.drops
            if drop.dt_match is True and drop.is_claimed is False
        ]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False
