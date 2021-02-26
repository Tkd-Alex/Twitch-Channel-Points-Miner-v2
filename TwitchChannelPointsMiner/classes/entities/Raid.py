class Raid(object):
    __slots__ = ["raid_id", "target_login"]

    def __init__(self, raid_id, target_login):
        self.raid_id = raid_id
        self.target_login = target_login

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.raid_id == other.raid_id
        else:
            return False
