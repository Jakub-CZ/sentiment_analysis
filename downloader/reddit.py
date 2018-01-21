import praw
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime, date, timezone, timedelta
import dateutil.parser as dateutil_parser
from json import dump, load, JSONEncoder

from common import enable_logging


class Post(namedtuple("Post", ("id", "date", "permalink", "title", "url"))):
    def __new__(cls, *args, **kwargs):
        """Converts ``date`` to a `datetime` instance."""
        if "date" in kwargs:
            _date = kwargs["date"]
        else:
            _date = args[1]
        if isinstance(_date, str):
            _date = dateutil_parser.parse(_date)
        elif isinstance(_date, (int, float)):
            _date = datetime.fromtimestamp(_date, timezone.utc)
        if "date" in kwargs:
            kwargs["date"] = _date
        else:
            args = list(args)
            args[1] = _date
        return super(Post, cls).__new__(cls, *args, **kwargs)


enable_logging("prawcore")
log = enable_logging("downloader.reddit")

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
def unseen_hot_posts(limit, history):
    seen = load_seen_posts(history)
    yield iter_unseen_posts(reddit.subreddit("cryptocurrency").hot(limit=limit), seen)  # 'seen' updated
    store_seen_posts(seen, history)


def main():
    with unseen_hot_posts(12, "seen.json") as posts:
        with open("hot.json", "w") as f:
            dump(list(posts), f, cls=DateTimeEncoder, indent=2)


def from_file(file):
    with open(file, "r") as f:
        posts = load(f)
    posts = [Post(*p) for p in posts]
    return posts


if __name__ == '__main__':
    # main()
    print(from_file("hot.json"))
