import json
import urllib.request

from common import enable_logging

log = enable_logging()

if __name__ == '__main__':
    with urllib.request.urlopen("https://min-api.cryptocompare.com/data/all/coinlist") as url:
        data = json.load(url)
        assert data["Response"].lower() == "success", "URL: %s\nResponse: %s\nMessage: %s" %\
                                                      (url.url, data["Response"], data["Message"])
    with open("coinlist.json", "w") as f:
        json.dump(data["Data"], f, indent=2)
