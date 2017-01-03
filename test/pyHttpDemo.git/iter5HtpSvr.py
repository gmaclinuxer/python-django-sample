
import json;
from asyncore import loop;
from asyncHttpServer import AsyncHttpServer, HttpHandler;

def index(req):
    return "Hello World, this is jimwu.";

def iterator2(req):
    if not req.has_key("param"):
        return "{}"
    if req["METHOD"] == "GET":
        return json.dumps(req["param"]);
    elif req["METHOD"] == "POST":
        import time;
        p = req["param"];
        p["time"] = time.time();
        return json.dumps(p);
    else:
        return "{}";

HttpHandler.parten = {
    "/": index,
    "/iterator2": iterator2,
}

if __name__ == '__main__':
    s = AsyncHttpServer(8080);
    loop(30, True);