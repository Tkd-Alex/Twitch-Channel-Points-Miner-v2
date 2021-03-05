import logging
import os
from pathlib import Path
from threading import Thread

from flask import Flask, Response, cli, render_template

from TwitchChannelPointsMiner.classes.Settings import Settings

cli.show_server_banner = lambda *_: None
logger = logging.getLogger(__name__)


def streamers_available():
    path = Settings.analytics_path
    return [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".json")
    ]


def read_json(streamer):
    path = Settings.analytics_path
    streamer = streamer if streamer.endswith(".json") else f"{streamer}.json"
    return Response(
        open(os.path.join(path, streamer)) if streamer in streamers_available() else [],
        status=200,
        mimetype="application/json",
    )


def index(refresh=5):
    return render_template(
        "charts.html",
        refresh=(refresh * 60 * 1000),
        streamers=",".join(streamers_available()),
    )


class AnalyticsServer(Thread):
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, refresh: int = 5):
        super(AnalyticsServer, self).__init__()

        self.host = host
        self.port = port
        self.refresh = refresh

        self.app = Flask(
            __name__,
            template_folder=os.path.join(Path().absolute(), "assets"),
            static_folder=os.path.join(Path().absolute(), "assets"),
        )
        self.app.add_url_rule("/", "index", index, defaults={"refresh": refresh})
        self.app.add_url_rule("/json/<string:streamer>", "json", read_json)

    def run(self):
        logger.info(
            f"Analytics running on http://{self.host}:{self.port}/",
            extra={"emoji": ":globe_with_meridians:"},
        )
        self.app.run(host=self.host, port=self.port, threaded=True)
