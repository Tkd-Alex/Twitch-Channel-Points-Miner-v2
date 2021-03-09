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

        self.chat_irc = None

    def run(self):
        self.chat_irc = Chat(self.username, self.token, self.channel)
        logger.info(
            f"Join IRC Chat: {self.channel}", extra={"emoji": ":speech_balloon:"}
        )
        self.chat_irc.start()

    def stop(self):
        if self.chat_irc is not None:
            logger.info(
                f"Leave IRC Chat: {self.channel}", extra={"emoji": ":speech_balloon:"}
            )
            self.chat_irc.die()
