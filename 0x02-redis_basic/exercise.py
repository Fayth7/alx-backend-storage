#!/usr/bin/env python3

import redis
import uuid
from typing import Callable
from functools import wraps

class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @staticmethod
    def count_calls(method: Callable) -> Callable:
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Increment count in Redis
            count_key = f"{key}_count"
            current_count = self._redis.incr(count_key)

            # Call the original method and return its result
            result = method(self, *args, **kwargs)
            return result

        return wrapper

    @staticmethod
    def call_history(method: Callable) -> Callable:
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Append input arguments to Redis list
            inputs_key = f"{key}:inputs"
            self._redis.rpush(inputs_key, str(args))

            # Execute the wrapped function to retrieve the output
            result = method(self, *args, **kwargs)

            # Store the output in the Redis list
            outputs_key = f"{key}:outputs"
            self._redis.rpush(outputs_key, str(result))

            return result

        return wrapper

    @count_calls
    @call_history
    def store(self, data):
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key, fn=None):
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn is not None else data

def replay(func):
    cache = Cache()
    key = func.__qualname__
    
    # Retrieve inputs and outputs from Redis lists
    inputs = cache._redis.lrange(f"{key}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{key}:outputs", 0, -1)

    print(f"{key} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{key}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")

# Test cases
cache = Cache()
cache.store("foo")
cache.store("bar")
cache.store(42)
replay(cache.store)
