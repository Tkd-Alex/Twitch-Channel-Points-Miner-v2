import time


class Streamer:
    def __init__(
        self,
        username,
        channel_id,
    ):
        self.username = username
        self.channel_id = channel_id
        self.is_online = False
        self.online_at = 0
        self.offline_at = 0
        self.channel_points = 0
        self.minute_watched_requests = None
        self.raid = None

        self.streamer_url = f"https://www.twitch.tv/{self.username}"
        self.char_url = f"https://www.twitch.tv/popout/{self.username}/chat?popout="

    def __repr__(self):
        return f"Streamer(username={self.username}, channel_id={self.channel_id}, is_online={self.is_online}, online_at={self.online_at}, offline_at={self.offline_at}, channel_points={self.channel_points})"

    def set_offline(self):
        self.offline_at = time.time()
        self.is_online = False

    def set_online(self):
        self.online_at = time.time()
        self.is_online = True
