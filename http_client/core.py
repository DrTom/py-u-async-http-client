try:
    import uasyncio as asyncio
except ImportError:
    import asyncio as asyncio
import logging as logging
import sys

logger = logging.getLogger("http_client")

def destructure_url(url):
    try:
        proto, _, host, path = url.split("/", 3)
    except ValueError:
        proto, _, host = url.split("/", 2)
        path = ""
    proto = proto.strip(':')
    if proto == "https":
        port = 443
        ssl = True
    else:
        port = 80
        ssl = False
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    return {"proto": proto,
            "host": host,
            "port": port,
            "path": path}

async def open_conn(req):
    url_params = destructure_url(req["url"])
    logger.debug('open_conn url_params: {}'.format(url_params))
    ssl = req.get('ssl') or (True if url_params['proto'] == 'https' else False)
    return await asyncio.open_connection(url_params['host'], url_params['port'], ssl=ssl)

async def close_conn(sr, sw):
    if sys.implementation.name == 'micropython':
        await sw.aclose()
        # await sr.aclose() # crashes, issue question pending
    elif sys.implementation.name == 'cpython':
        sw.close()
        await sw.wait_closed()
    else:
        raise "{} is not supported yet".format(sys.implementation.name)

def build_head(req):
    url = destructure_url(req['url'])
    method = req.get("method","GET")
    body = req.get("body",None)
    headers = req.get("headers",{})
    head = []
    head.append("%s /%s HTTP/1.0" % (method, url['path']))
    head.append("Host: %s" % url['host'])
    for k in headers: head.append("%s: %s" % (k, headers[k]))
    if body: head.append("Content-Length: %d" % len(body))
    head.append("\r\n")
    return "\r\n".join(head).encode()

async def send_req(sw,req):
    logger.debug("send_req req: {}".format(req))
    head = build_head(req)
    logger.debug("HEAD: {}".format(head))
    body = req.get("body",None)
    body = body and body.encode()
    logger.debug("BODY: {}".format(body))
    if sys.implementation.name == 'micropython':
        await sw.awrite(head)
        if body: await sw.awrite(body)
    elif sys.implementation.name == 'cpython':
        sw.write(head)
        if body:
            sw.write(body)
        await sw.drain()
    else:
        raise "{} is not supported yet".format(sys.implementation.name)

async def get_status(sr):
    try:
        status = {}
        status_line = await sr.readline()
        logger.debug("status_line: {}".format(status_line))
        status_v, status_code_s, *status_rest = status_line.split(None, 2)
        status["http_version"]= status_v.decode()
        status["code"]= int(status_code_s)
        if len(status_rest) > 2:
            status['reason_phrase'] = status_rest[2].rstrip()
        return status
    except Exception as ex:
        raise ValueError("Failed to parse the HTTP status line: {}".format(status_line)) from ex

async def get_resp(sr, req):
    resp = {"status": {},
            "headers": {},
            "body": None}
    resp["status"] = await get_status(sr)
    while True:
        header_line = await sr.readline()
        if not header_line or header_line == b'\r\n':
            break
        hk, hm = header_line.decode().split(":", 1)
        resp["headers"][hk]=hm.strip()
    resp["body"] = await sr.read()
    return resp

async def request(req):
    logger.debug(req)
    try:
        sr, sw = await open_conn(req)
        try:
            await send_req(sw,req)
            resp = await get_resp(sr, req)
            return resp
        except Exception as ex:
            return {"status":{"code":900},
                    "send/rec error ": ex}
        finally:
            await close_conn(sr, sw)
    except Exception as ex:
        return {"status":{"code":900},
                "connection error ": ex}

