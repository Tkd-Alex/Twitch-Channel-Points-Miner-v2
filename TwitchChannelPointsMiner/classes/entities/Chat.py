import logging

from irc.bot import SingleServerIRCBot

from TwitchChannelPointsMiner.constants import IRC, IRC_PORT

logger = logging.getLogger(__name__)


class Chat(SingleServerIRCBot):
    def __init__(self, username, token, channel):
        self.token = token
        self.channel = "#" + channel
        self.__active = False

        super(Chat, self).__init__(
            [(IRC, IRC_PORT, f"oauth:{token}")], username, username
        )

    def on_welcome(self, client, event):
        client.join(self.channel)

    def start(self):
        self.__active = True
        self._connect()
        while self.__active:
            self.reactor.process_once(timeout=0.2)

    def die(self, msg="Bye, cruel world!"):
        self.connection.disconnect(msg)
        self.__active = False

    """
    def on_join(self, connection, event):
        logger.info(f"Event: {event}", extra={"emoji": ":speech_balloon:"})

    def on_pubmsg(self, client, message):
        logger.info(f"Message: {message}", extra={"emoji": ":speech_balloon:"})
    """
