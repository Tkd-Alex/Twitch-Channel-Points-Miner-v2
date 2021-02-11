from datetime import datetime


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
            else int(
                (self.current_minutes_watched / self.current_minutes_watched) * 100
            )
        )

    def __repr__(self):
        return f"Drop(id={self.id}, name={self.name}, benefit={self.benefit}, minutes_required={self.minutes_required}, has_preconditions_met={self.has_preconditions_met}, current_minutes_watched={self.current_minutes_watched}, drop_instance_id={self.drop_instance_id}, is_claimed={self.is_claimed})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False
