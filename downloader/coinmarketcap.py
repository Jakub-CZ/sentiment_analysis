import json
import os
import urllib.request
from typing import Dict

from common import enable_logging

log = enable_logging("downloader.coinmarketcap")
coinlist_file = os.path.realpath("coinlist.json")


def download_top_coins():
    with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=200") as url:
        data = json.load(url)
        assert len(data) == 200, "Something strange was returned:\n%s..." % str(data)[:500]
    with open(coinlist_file, "w") as f:
        json.dump(data, f, indent=2)


def get_top_coins() -> Dict[str, str]:
    """Mapping cryptocurrency symbols to names"""
    if not os.path.exists(coinlist_file):
        download_top_coins()
    with open(coinlist_file, "r") as f:
        coins = json.load(f)
    return {c["symbol"]: c["name"] for c in coins}


if __name__ == '__main__':
    print(get_top_coins())
