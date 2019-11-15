try:
    import json as json
except ImportError:
    import ujson as json

def prepare_request(request):
    body = request.get("body")
    if type(body) is dict or isinstance(body,list):
        request["body"] = json.dumps(body)
        headers = request.get("headers",{})
        headers["Content-Type"] = "application/json"
        request["headers"] = headers
    return request

def prepare_resonse(response):
    if response.get("headers",{}).get("Content-Type","").startswith("application/json"):
        response["body"] = json.loads(response.get("body","null"))
    return response

async def _wrap(request,send):
    return prepare_resonse(await send(prepare_request(request)))

async def wrap(send):
    async def s(request):
        return await _wrap(request,send)
    return s
