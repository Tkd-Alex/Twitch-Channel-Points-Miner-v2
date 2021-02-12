from datetime import datetime

from TwitchChannelPointsMiner.classes.Settings import Settings


class Drop(object):
    def __init__(self, dict):
        self.id = dict["id"]
        self.name = dict["name"]
        self.benefit = ", ".join(
            list(set([bf["benefit"]["name"] for bf in dict["benefitEdges"]]))
        )
        self.minutes_required = dict["requiredMinutesWatched"]

        self.has_preconditions_met = False
        self.current_minutes_watched = 0
        self.drop_instance_id = None
        self.is_claimed = False
        self.is_claimable = False

        self.end_at = datetime.strptime(dict["endAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.start_at = datetime.strptime(dict["startAt"], "%Y-%m-%dT%H:%M:%SZ")
        self.dt_match = self.start_at < datetime.now() < self.end_at

    def update(
        self,
        progress,
    ):
        self.has_preconditions_met = progress["hasPreconditionsMet"]
        self.current_minutes_watched = progress["currentMinutesWatched"]
        self.drop_instance_id = progress["dropInstanceID"]
        self.is_claimed = progress["isClaimed"]
        self.percentage_progress = (
            0
            if self.current_minutes_watched == 0
            else int((self.current_minutes_watched / self.minutes_required) * 100)
        )
        self.is_claimable = (
            self.is_claimed is False and self.drop_instance_id is not None
        )

    def __repr__(self):
        return f"Drop(id={self.id}, name={self.name}, benefit={self.benefit}, minutes_required={self.minutes_required}, has_preconditions_met={self.has_preconditions_met}, current_minutes_watched={self.current_minutes_watched}, percentage_progress={self.percentage_progress}%, drop_instance_id={self.drop_instance_id}, is_claimed={self.is_claimed})"

    def __str__(self):
        return (
            f"{self.name} ({self.benefit}) {self.current_minutes_watched}/{self.minutes_required} ({self.percentage_progress}%)"
            if Settings.logger.less
            else self.__repr__()
        )

    def progress_bar(self):
        progress = self.percentage_progress // 2
        remaining = (100 - self.percentage_progress) // 2
        if remaining + progress < 50:
            remaining += 50 - (remaining + progress)
        return (
            ("|" + ("█" * progress) + (" " * remaining) + "|")
            + f"\t{self.percentage_progress}% [{self.current_minutes_watched}/{self.minutes_required}]"
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False
