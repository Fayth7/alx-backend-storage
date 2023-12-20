#!/usr/bin/env python3
""" Redis Module """

import requests
import redis
from functools import wraps
from typing import Callable

# Create a Redis connection
redis_client = redis.Redis()

def count_accesses(url: str) -> int:
    count_key = f"count:{url}"
    return redis_client.incr(count_key)

def cache_page(url: str, content: str, expiration_time: int = 10):
    cache_key = f"cache:{url}"
    redis_client.setex(cache_key, expiration_time, content)

def get_page(url: str) -> str:
    # Check if the content is cached
    cache_key = f"cache:{url}"
    cached_content = redis_client.get(cache_key)
    if cached_content is not None:
        # Content found in cache, return it
        return cached_content.decode('utf-8')

    # Content not in cache, make a request
    response = requests.get(url)
    content = response.text

    # Cache the content and track the access count
    count = count_accesses(url)
    cache_page(url, content)

    print(f"Accessed {url} {count} times.")

    return content

# Example usage
if __name__ == "__main__":
    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    
    # Access the slow URL multiple times
    for _ in range(5):
        get_page(slow_url)

    # Access a normal URL
    normal_url = "https://www.example.com"
    get_page(normal_url)
