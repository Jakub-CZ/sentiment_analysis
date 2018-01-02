import praw
import logging
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime, date, timezone, timedelta
import dateutil.parser as dateutil_parser
from json import dump, load, JSONDecoder, JSONEncoder


Post = namedtuple("Post", ("id", "date", "permalink", "title", "url"))


def _enable_logging(logger_name="prawcore", level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


_enable_logging()
log = _enable_logging(logger_name=__name__)

reddit = praw.Reddit(client_id="ljUsVQ0ChTw8AQ",
                     client_secret="wtjGEdkz4tRfsEHBWo4bH8YzBW8",
                     user_agent="windows:trend_analysis:v0.1 (by /u/jloucky)")


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        super(DateTimeEncoder, self).default(obj)


def iter_unseen_posts(listing, seen):
    """Updates 'seen' with new posts."""
    for post in listing:
        if post.id in seen or post.stickied:
            print("- ignoring: %s" % post.title)
            continue
        print("      NEW : %s" % post.title)
        p = Post(id=post.id, date=datetime.fromtimestamp(post.created_utc, timezone.utc),
                 permalink=post.permalink, title=post.title, url=post.url)
        yield p
        seen[p.id] = p.date


def store_seen_posts(seen, history_file, max_days=3):
    now = datetime.now(timezone.utc)
    seen = {k: v for k, v in seen.items() if now - v < timedelta(days=max_days)}  # drop old posts
    log.debug("Saving %d posts younger than %d days" % (len(seen), max_days))
    with open(history_file, "w") as f:
        dump(seen, f, cls=DateTimeEncoder, indent=2)


def load_seen_posts(history_file):
    seen = {}
    try:
        with open(history_file, "r") as f:
            seen = load(f)  # TODO: parse datetime using JSONDecoder
        log.debug("Loaded %d previously seen posts" % len(seen))
    except FileNotFoundError as e:
        log.warning("Error while trying to load previously seen posts:\n%s" % e)
    seen = {k: dateutil_parser.parse(v) for k, v in seen.items()}  # parsing date here temporarily
    return seen


@contextmanager
def unseen_hot_posts(history):
    seen = load_seen_posts(history)
    yield iter_unseen_posts(reddit.subreddit("cryptocurrency").hot(limit=12), seen)  # 'seen' updated
    store_seen_posts(seen, history)


def main():
    with unseen_hot_posts("seen.json") as posts:
        with open("hot.json", "w") as f:
            dump(list(posts), f, cls=DateTimeEncoder, indent=2)


if __name__ == '__main__':
    main()
