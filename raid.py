from claim_bonus import post_gql_request


class Raid:
    def __init__(self, raid_id, target_login):
        self.raid_id = raid_id
        self.target_login = target_login

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.raid_id == other.raid_id
        else:
            return False


raid_id_for_streamer = {}


# streamer_login is going to raid someone
def update_raid(streamer_login, raid):
    if raid_id_for_streamer.get(streamer_login) != raid:
        raid_id_for_streamer[streamer_login] = raid
        post_gql_request(
            {"operationName": "JoinRaid",
             "variables": {"input": {"raidID": raid.raid_id}},
             "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "c6a332a86d1087fbbb1a8623aa01bd1313d2386e7c63be60fdb2d1901f01a4ae"}}})

        print(f"Joining raid from {streamer_login} to {raid.target_login}!")