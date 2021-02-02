import logging
import os
from multiprocessing import Process
from pathlib import Path

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


def index():
    return render_template("charts.html", streamers=",".join(streamers_available()))


class AnalyticsServer(Process):
    def __init__(self, host="127.0.0.1", port=5000):
        super(AnalyticsServer, self).__init__()

        self.host = host
        self.port = port

        self.app = Flask(
            __name__,
            template_folder=os.path.join(Path().absolute(), "assets"),
            static_folder=os.path.join(Path().absolute(), "assets"),
        )
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule("/json/<string:streamer>", "json", read_json)

    def run(self):
        logger.info(
            f"Running on http:/{self.host}:{self.port}/",
            extra={"emoji": ":globe_with_meridians:"},
        )
        self.app.run(host=self.host, port=self.port, threaded=True)
