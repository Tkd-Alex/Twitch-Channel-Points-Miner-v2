import json
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


def read_json(streamer, return_response=True):
    path = Settings.analytics_path
    streamer = streamer if streamer.endswith(".json") else f"{streamer}.json"
    if return_response is True:
        return Response(
            open(os.path.join(path, streamer))
            if streamer in streamers_available()
            else [],
            status=200,
            mimetype="application/json",
        )
    return (
        json.loads(open(os.path.join(path, streamer)).read())
        if streamer in streamers_available()
        else []
    )


def get_challenge_points(streamer):
    datas = read_json(streamer, return_response=False)
    if datas != {}:
        return datas["series"][-1]["y"]
    return 0


def json_all():
    return Response(
        json.dumps(
            [
                {
                    "name": streamer.strip(".json"),
                    "data": read_json(streamer, return_response=False),
                }
                for streamer in streamers_available()
            ]
        ),
        status=200,
        mimetype="application/json",
    )


def index(refresh=5):
    return render_template(
        "charts.html",
        refresh=(refresh * 60 * 1000),
    )


def streamers():
    return Response(
        json.dumps(
            [
                {"name": s, "points": get_challenge_points(s)}
                for s in sorted(streamers_available())
            ]
        ),
        status=200,
        mimetype="application/json",
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
        self.app.add_url_rule("/streamers", "streamers", streamers)
        self.app.add_url_rule("/json/<string:streamer>", "json", read_json)
        self.app.add_url_rule("/json_all", "json_all", json_all)

    def run(self):
        logger.info(
            f"Analytics running on http://{self.host}:{self.port}/",
            extra={"emoji": ":globe_with_meridians:"},
        )
        self.app.run(host=self.host, port=self.port, threaded=True)
