import requests
from types import SimpleNamespace

def fetch_review_counts(gr_key, isbn):
    print("Fetching Goodreads review counts for", isbn)
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": gr_key, "isbns": isbn})
    return SimpleNamespace(**response.json()["books"][0])