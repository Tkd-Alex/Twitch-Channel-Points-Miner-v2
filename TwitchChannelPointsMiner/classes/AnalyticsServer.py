import os
from pathlib import Path

from flask import Flask, Response, render_template  # , cli

from TwitchChannelPointsMiner.classes.Settings import Settings


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


# cli.show_server_banner = lambda *_: None


class AnalyticsServer(object):
    def __init__(self):
        self.app = Flask(
            __name__,
            template_folder=os.path.join(Path().absolute(), "assets"),
            static_folder=os.path.join(Path().absolute(), "assets"),
        )
        self.app.add_url_rule("/", "index", index)
        self.app.add_url_rule("/json/<string:streamer>", "json", read_json)

    def run(self):
        self.app.run()
