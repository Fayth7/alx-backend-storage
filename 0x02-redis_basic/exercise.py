#!/usr/bin/env python3

from typing import Callable, Optional, Union
from uuid import uuid4
import redis
from functools import wraps

def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = f"{method.__qualname__}:calls"
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    key = method.__qualname__
    inputs_key, outputs_key = f"{key}:inputs", f"{key}:outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(inputs_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(outputs_key, str(result))
        return result

    return wrapper

def replay(method: Callable) -> None:
    name = method.__qualname__
    cache = redis.Redis()
    calls_key = f"{name}:calls"
    calls = cache.get(calls_key).decode("utf-8")
    
    print(f"{name} was called {calls} times:")
    
    inputs = cache.lrange(f"{name}:inputs", 0, -1)
    outputs = cache.lrange(f"{name}:outputs", 0, -1)
    
    for inp, out in zip(inputs, outputs):
        print(f"{name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")

class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        value = self._redis.get(key)
        return fn(value) if fn else value

    def get_str(self, key: str) -> str:
        return self.get(key, lambda value: value.decode('utf-8'))

    def get_int(self, key: str) -> int:
        value = self.get(key, lambda value: int(value.decode('utf-8', 'ignore')) if value else 0)
        return value
