import json
import os
import urllib.request
from typing import Dict

from common import enable_logging

log = enable_logging("downloader.coinmarketcap")
coinlist_file = os.path.realpath("coinlist.json")
blacklist = ["BitConnect"]


def download_top_coins(limit=200):
    with urllib.request.urlopen("https://api.coinmarketcap.com/v1/ticker/?limit=%d" % limit) as url:
        data = json.load(url)
        assert len(data) == limit, "Something strange was returned:\n%s..." % str(data)[:500]
    with open(coinlist_file, "w") as f:
        json.dump(data, f, indent=2)


def get_top_coins() -> Dict[str, str]:
    """Mapping cryptocurrency symbols to names"""
    # TODO: redownload periodically, but keep old if it failed
    if not os.path.exists(coinlist_file):
        download_top_coins()
    with open(coinlist_file, "r") as f:
        coins = json.load(f)
    return {c["symbol"]: c["name"] for c in coins if c["name"] not in blacklist}


def get_coin_mappings():
    all_coins = get_top_coins()  # symbol -> name
    all_coin_names = {n.lower(): s for s, n in all_coins.items()}  # lower case name -> symbol

    # aliases:
    all_coin_names["bcash"] = "BCH"
    all_coin_names["raiblocks"] = "NANO"
    all_coin_names["walton"] = "WTC"
    all_coin_names_lower_sorted_by_len = sorted(all_coin_names, key=len, reverse=True)

    return all_coins, all_coin_names, all_coin_names_lower_sorted_by_len


if __name__ == '__main__':
    print(get_top_coins())
