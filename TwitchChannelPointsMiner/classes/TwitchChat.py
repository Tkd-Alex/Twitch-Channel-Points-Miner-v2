import logging
from threading import Thread

from TwitchChannelPointsMiner.classes.entities.Chat import Chat

logger = logging.getLogger(__name__)


class TwitchChat(Thread):
    def __deepcopy__(self, memo):
        return None

    def __init__(self, username, token, channel):
        super(TwitchChat, self).__init__()
        self.token = token
        self.username = username
        self.channel = channel

    def run(self):
        # Create IRC bot connection
        try:
            IRC = Chat(self.username, self.token, self.channel)
            IRC.start()
        except KeyboardInterrupt:
            None  # dont handle KeyboardInterruption here
