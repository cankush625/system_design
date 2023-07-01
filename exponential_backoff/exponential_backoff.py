from functools import wraps
import random
import time
import requests


# Ref: https://cloud.google.com/iot/docs/how-tos/exponential-backoff

def retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        retry_count = 0
        max_retry = 10
        maximum_backoff = 64
        exponent = 0
        exponential_backoff = 0
        while True:
            try:
                print(f"Retry {retry_count}, exponential backoff time {exponential_backoff}")
                time.sleep(exponential_backoff)
                return func(*args, *kwargs)
            except ConnectionError:
                retry_count += 1
                # Client should not be able to retry after the max retry
                # limit is reached
                if retry_count > max_retry:
                    raise ConnectionError("cannot connect to the website.")
                # If exponential backoff time is reached to the maximum
                # backoff time then we don't need to increase the exponential
                # backoff time. The subsequent request can wait for the
                # maximum backoff time.
                if exponential_backoff < maximum_backoff:
                    # Add random milliseconds to the exponential backoff
                    # time. This is used to avoid the problem where if many
                    # clients are synchronized by some situation and all
                    # retry at once.
                    exponential_backoff = (2 ** exponent) + (random.randint(0, 1000) / 1000)
                    exponent += 1
                else:
                    exponential_backoff = maximum_backoff + (random.randint(0, 1000) / 1000)
    return wrapper


@retry
def fetch_data():
    url = "https://example.com"
    res = requests.get(url)
    if not res.ok:
        raise ConnectionError()
    return res.content


data = fetch_data()
print(data)
