import requests
from types import SimpleNamespace


def fetch_review_counts(gr_key, isbn):
    """ Gets review count and review average from goodreads
    for a book by specified ISBN. """
    print("Fetching Goodreads review counts for", isbn)
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": gr_key, "isbns": isbn})
    return SimpleNamespace(**res.json()["books"][0])
