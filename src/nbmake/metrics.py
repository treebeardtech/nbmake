import json
import os
import platform
import sys
import time
import urllib.request


def submit_event():
    """We collect anonymous usage metrics to improve nbmake.

    You can disable them by setting the environment variable NBMAKE_METRICS=0.
    """
    mixpanel_token = "8440a5d8fa0ec1d43b6bcaf76037fae7"
    url = "https://api-eu.mixpanel.com/track"

    payload = [
        {
            "event": "Invocation",
            "properties": {
                "token": mixpanel_token,
                "$os": platform.system(),
                "time": int(time.time()),
                "platform": platform.platform(),
                "python": sys.version,
                "ci": os.getenv("CI", False) and True,
            },
        }
    ]
    headers = {
        "accept": "text/plain",
        "content-type": "application/json",
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf8"), headers=headers
    )
    response = urllib.request.urlopen(req, timeout=1.0)

    return response.read().decode("utf8")
