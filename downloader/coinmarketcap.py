import json
import urllib.request

from common import enable_logging

log = enable_logging()

if __name__ == '__main__':
    with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=200") as url:
        data = json.load(url)
        assert len(data) == 200, "Something strange was returned:\n%s..." % str(data)[:500]
    with open("coinlist2.json", "w") as f:
        json.dump(data, f, indent=2)
