import irc.bot

from TwitchChannelPointsMiner.constants import IRC, IRC_PORT


class Chat(irc.bot.SingleServerIRCBot):
    def __init__(self, username, token, channel):
        self.token = token
        self.channel = "#" + channel

        # Create IRC bot connection
        irc.bot.SingleServerIRCBot.__init__(
            self, [(IRC, IRC_PORT, "oauth:" + token)], username, username
        )

    def on_welcome(self, c, e):
        # You must request specific capabilities before you can use them
        c.join(self.channel)
