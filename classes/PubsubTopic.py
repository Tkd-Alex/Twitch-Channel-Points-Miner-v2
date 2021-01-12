class PubsubTopic:
    def __init__(self, topic, channel_login=None):
        self.topic = topic
        self.channel_login = channel_login

    def is_user_topic(self):
        return self.channel_login is None

    def __str__(self):
        if self.is_user_topic():
            return f"{self.topic}.{get_user_id()}"
        else:
            return f"{self.topic}.{get_channel_id(self.channel_login)}"