import logging
import sys


def enable_logging(logger_name=__name__, level=logging.DEBUG):
    logging.basicConfig(level=level,
                        stream=sys.stdout,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(logger_name)
    # logger.setLevel(level)
    return logger


# TODO: implement re-analysis of old results in 'analysis.json'
# TODO: Mask 'Ledger Nano'
def main():
    import os, json
    from downloader.coinmarketcap import get_top_coins

    log = enable_logging("analyze")
    all_coins = get_top_coins()  # symbol -> name
    all_coin_names = {n.lower(): s for s, n in all_coins.items()}  # lower case name -> symbol
    all_coin_names["raiblocks"] = "XRB"
    all_coin_names_lower_sorted_by_len = sorted(all_coin_names, key=len, reverse=True)

    from pprint import pprint
    from collections import namedtuple
    from analyze import analyze_post
    FakePost = namedtuple("FakePost", "title")
    with open(os.path.realpath("analysis.json"), "r") as f:
        analysis = json.load(f)
    diffs = []
    for d in analysis:
        title = d["post"][3]
        old_coins = set(all_coin_names[name.lower()] for name in d["coins"])
        a = analyze_post(FakePost(title), all_coins, all_coin_names, all_coin_names_lower_sorted_by_len,
                         get_body=False)
        new_coins = set(a["coins"])
        diff = new_coins.symmetric_difference(old_coins)
        if diff:
            diffs.append("%s\n  Old: %s \t New: %s\n Diff: %s" % (title, old_coins, new_coins, diff))
    print("\n".join(diffs))

    ###############
    # for c1 in all_coins.values():
    #     for c2 in all_coins.values():
    #         if c2 != c1 and c2 in c1:
    #             print("'%s' in '%s'" % (c2, c1))
    ###############
    # analysis_file = os.path.realpath("analysis.json")
    # log.info("Opening '%s'" % analysis_file)
    # with open(analysis_file, "r") as f:
    #     analysis = json.load(f)


if __name__ == '__main__':
    main()
