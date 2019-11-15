import http_client.core as http_client
import http_client.json_middleware as json_middleware

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio as asyncio

import logging

import sys

# http_client.logger.setLevel(logging.DEBUG)

if sys.implementation.name == 'cpython':
    http_client.logger.addHandler(logging.StreamHandler())

res_dict= {"error": "Request has not been executed."}
req_dict= {
        "url": "https://xkcd.com/info.0.json"
        "headers": {
            "Accept": "application/json" }}

loop = asyncio.get_event_loop()

async def request(req_dict):
    r = await json_middleware.wrap(http_client.request)
    # r = await my_middleware.wrap(r) # weave in more middleware here
    return await r(req_dict)

async def get_current_xkcd_metadata():
    global res_dict
    res_dict = await request(req_dict)

loop.run_until_complete(get_current_xkcd_metadata())

print("response dict: {}".format(res_dict))

