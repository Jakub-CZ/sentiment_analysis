from nltk import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from common import enable_logging
from downloader.coinmarketcap import get_top_coins
from downloader.reddit import from_file

log = enable_logging("analyze")
sia = SIA()

if __name__ == '__main__':
    all_coins = get_top_coins()
    all_coin_names = {n.lower(): n for n in all_coins.values()}
    for post in from_file("hot.json"):
        title = post.title
        log.info(title)
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
        log.debug(sia.polarity_scores(title))

