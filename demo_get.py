import http_client.core as http_client
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio as asyncio

req_dict= {"url": "https://xkcd.com/info.0.json"}

loop = asyncio.get_event_loop()

async def get_current_xkcd_metadata():
    global res_dict
    res_dict = await http_client.request(req_dict)

loop.run_until_complete(get_current_xkcd_metadata())

print("response dict: {}".format(res_dict))

