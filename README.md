A asynchronous HTTP Client for Micro- and CPython
=================================================

This repository contains code of minimalistic asynchronous http-client for
Python. It targets primarily MicroPython but it will also run on standard
Python, also known as cPython.


Dependencies
------------

* MicroPython (1.11 tested) or Python (3.7 tested)
* logging, see [micropython-logging] for MicroPython
* asyncio, or [uasyncio] for MicroPython

Development of the [uasyncio] library for MicroPython seems to be
fragmented and in flux a this time. This project is tested against
the [uasyncio] from https://pypi.org.

However, there is ongoing work to provide a more unified uasyncio
API with respect to asyncio in CPython ([1], [2]). This library
will very likely support this new version in the future.

Usage
-----

### GET Request

See [./demo_get.py](demo_get.py).

The `request` "function" (more precisely it is an asyncio coroutine) from
[http_client.core] takes the "request dictionary" as its sole argument.

    await http_client.request({"url": "https://xkcd.com/info.0.json"})

The `url` is the only required key. It returns a "response dictionary".  Note
that the body withing is a byte array.


### JSON GET Request

Sending or retrieving JSON is a very common task. The focus of
[http_client.core] is to perform and process basic http requests. Its design
allows it to be easily extended by functional wrapping. To perform JSON
requests and to the end of giving an example [http_client.json_middleware.py]
is provided. The following shows how to apply it:

~~~python
async def request(req_dict):
    r = await json_middleware.wrap(http_client.request)
    # r = await my_middleware.wrap(r) # weave in more middleware here
    return await r(req_dict)

# then in some async fun:

    await request(req_dict)
~~~

See also [./demo_get_json.py](demo_get_json.py).

[http_client.json_middleware.py] transforms the body in the response dictionary
into Python data.

It does not modify/set the `Accept` header. The request dictionary should
contain it. However, many APIs are JSON only and work fine without `Accept`
header, see the example above.

~~~python
req_dict= {
        "url": "https://xkcd.com/info.0.json"
        "headers": {
            "Accept": "application/json" }}
~~~

### PUT, POST and other HTTP-Verbs and Nouns

The request dictionary supports the keyword `method` for sending other HTTP
methods or nouns. Here is an example with `PUT`:

~~~python
{ "url": "http://{{BRIDGE_IP}}/api/{{API_KEY}}/groups/{{HUE_GROUP_ID}}/action",
  "headers": { "Accept": "application/json" }},
  "method": "PUT",
  "body": {"on":True, "bri": 128}}
~~~

Note that the body above is Python data. This will only work with some
additional middleware. See the previous example.






[http_client.core]: ./http_client/core.py
[http_client.json_middleware.py]: ./http_client/json_middleware.py

[micropython-logging]: https://pypi.org/project/micropython-logging/
[uasyncio]: https://pypi.org/project/micropython-uasyncio/

[1]: https://github.com/peterhinch/micropython-async/issues/30
[2]: https://github.com/micropython/micropython/pull/5332
