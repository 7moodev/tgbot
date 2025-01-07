import os
import requests
import time
import base58
import functools
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession, ClientError
import math
import aiohttp


heliusrpc = os.environ.get('heliusrpc')
quicknoderpc = os.environ.get('solrpc')
def timing_decorator(func):
    # Track recursion depth to create indented output for nested calls
    timing_decorator.level = getattr(timing_decorator, 'level', 0)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        indent = "  " * timing_decorator.level
        timing_decorator.level += 1
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.time()
            timing_decorator.level -= 1
        
        execution_time = end_time - start_time
        print(f"{indent}Function '{func.__name__}' took {execution_time:.2f} seconds to execute")
        return result
    return wrapper

def get_rpc():
    Random = random.randint(0, 1)
    if Random == 0:
        print("Using heliusrpc")
        return heliusrpc
    else:
        print("Using quicknoderpc")
        return quicknoderpc


