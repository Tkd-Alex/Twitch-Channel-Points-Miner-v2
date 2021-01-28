import json

from base64 import b64encode


class RequestInfo:
    def __init__(self, url):
        self.url = url
        self.payload = None

    def encode_payload(self):
        json_event = json.dumps(self.payload, separators=(",", ":"))
        return {"data": (b64encode(json_event.encode("utf-8"))).decode("utf-8")}