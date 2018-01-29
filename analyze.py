import json
from typing import List, Dict

import os
from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from common import enable_logging
from downloader.coinmarketcap import get_top_coins
from downloader.reddit import unseen_hot_posts, reddit, DateTimeEncoder

log = enable_logging("analyze")
sia = SIA()


def analyze_posts(posts):
    all_coins = get_top_coins()
    all_coin_names = {n.lower(): n for n in all_coins.values()}
    analysis = []  # type: List[Dict]
    analysis_file = os.path.realpath("analysis.json")
    log.info("Opening '%s'" % analysis_file)
    try:
        with open(analysis_file, "r") as f:
            analysis = json.load(f)
    except FileNotFoundError as e:
        log.warning("Error while trying to load previous analysis:\n%s" % e)
    for post in posts:
        # TODO: filter out some flairs
        title = post.title
        words = word_tokenize(title)
        related_coins = set()
        for w in words:
            if w.isupper() and w in all_coins:
                related_coins.add(all_coins[w])
                log.debug(w)
            elif w.lower() in all_coin_names:
                related_coins.add(all_coin_names[w.lower()])
                log.debug(w)
        log.info(related_coins)
        sentiment_title = sia.polarity_scores(title)
        log.info(sentiment_title)
        body = reddit.submission(post.id).selftext
        sentiment_body = {}
        if len(body) > 16:
            sentiment_body = sia.polarity_scores(body)
            log.info(sentiment_body)
        analysis.append({"post": post, "body": body, "coins": list(related_coins),
                         "sentiment_title": sentiment_title["compound"],
                         "sentiment_body": sentiment_body.get("compound")})
    analysis_json = json.dumps(analysis, cls=DateTimeEncoder, indent=2)
    with open(analysis_file, "w") as f:
        f.write(analysis_json)


if __name__ == '__main__':
    with unseen_hot_posts(50, os.path.realpath("seen.json")) as posts:
        analyze_posts(posts)
