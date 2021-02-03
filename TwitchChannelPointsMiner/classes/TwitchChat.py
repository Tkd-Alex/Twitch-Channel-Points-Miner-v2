import logging
from multiprocessing import Process

from TwitchChannelPointsMiner.classes.entities.Chat import Chat

logger = logging.getLogger(__name__)


class ChatSettings(object):
    def __init__(
        self,
        username: str = None,
        token: str = None,
    ):
        self.username = username
        self.token = token


class TwitchChat(Process):
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
