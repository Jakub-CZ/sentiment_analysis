import json
from typing import List, Dict
import os

from itertools import chain
from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.tokenize.util import align_tokens

from common import enable_logging
from downloader.coinmarketcap import get_coin_mappings
from downloader.reddit import unseen_hot_posts, reddit, DateTimeEncoder, Post

log = enable_logging("analyze")
sia = SIA()
# ignored when capitalized like this
generic_names = ["verify", "shift", "chips", "ICOs", "Blue", "life", "rise", "storm"]


def analyze_posts(posts):
    all_coins, all_coin_names, all_coin_names_lower_sorted_by_len = get_coin_mappings()

    analysis = []  # type: List[Dict]
    analysis_file = os.path.realpath("analysis.json")
    log.info("Opening '%s'" % analysis_file)
    try:
        with open(analysis_file, "r") as f:
            analysis = json.load(f)
    except FileNotFoundError as e:
        log.warning("Error while trying to load previous analysis:\n%s" % e)
    for post in posts:
        # TODO: filter out some flairs (COMEDY, FUN, ...)
        analysis.append(analyze_post(post, all_coins, all_coin_names, all_coin_names_lower_sorted_by_len))
    analysis_json = json.dumps(analysis, cls=DateTimeEncoder, indent=2)
    with open(analysis_file, "w") as f:
        f.write(analysis_json)


def reanalyze_posts():
    all_coins, all_coin_names, all_coin_names_lower_sorted_by_len = get_coin_mappings()

    analysis_file = os.path.realpath("analysis.json")
    log.info("Opening '%s'" % analysis_file)
    with open(analysis_file, "r") as f:
        analysis = json.load(f)
    reanalysis = []
    for d in analysis:
        post = Post(*d["post"])
        reanalysis.append(analyze_post(post, all_coins, all_coin_names, all_coin_names_lower_sorted_by_len,
                                       _body=d["body"]))
    reanalysis_json = json.dumps(reanalysis, cls=DateTimeEncoder, indent=2)
    with open(analysis_file, "w") as f:
        f.write(reanalysis_json)


def analyze_post(post, symbol2name, lname2symbol, lnames_sorted, _body=None):
    title = post.title  # type: str
    title = title.replace("``", '"').replace("''", '"')
    words = word_tokenize(title)
    log.info(title)
    words = ['"' if w in ["``", "''"] else w for w in words]
    word_boundaries = list(chain.from_iterable(align_tokens(words, title)))
    related_coins = set()
    for w in words:  # 1. - identify symbols in all caps
        w = {"XRB": "NANO"}.get(w) or w  # TODO: refactor handling of aliases
        if w.isupper() and w in symbol2name:
            related_coins.add(w)
            log.debug(w)
    ltitle = title.lower()
    ltitle.replace("ledger nano", "****** ****")  # TODO: refactor phrase masking
    for name in lnames_sorted:  # 2. - identify names
        start = ltitle.find(name)
        end = start + len(name)
        if start >= 0 and start in word_boundaries and end in word_boundaries:
            # names should start/end on word boundaries (not a mere substring)
            if title[start:end] in generic_names:
                # coin name is a generic word (or otherwise blacklisted - taking capitalization into account)
                continue
            related_coins.add(lname2symbol[name])
            log.debug(name)
            ltitle = ltitle.replace(name, "*" * len(name))
    log.info(related_coins)
    sentiment_title = sia.polarity_scores(post.title)
    log.info(sentiment_title)
    body = reddit.submission(post.id).selftext if _body is None else _body
    sentiment_body = {}
    if len(body) > 16:
        sentiment_body = sia.polarity_scores(body)
        log.info(sentiment_body)
    return {"post": post, "body": body, "coins": list(related_coins),
            "sentiment_title": sentiment_title["compound"],
            "sentiment_body": sentiment_body.get("compound")}


if __name__ == '__main__':
    with unseen_hot_posts(50, os.path.realpath("seen.json")) as posts:
        analyze_posts(posts)
