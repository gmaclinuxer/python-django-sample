
from HttpServer import HttpServer, BaseHandler;


import json;

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

BaseHandler.parten = {
    "/": index,
    "/iterator2": iterator2,
}

if __name__ == '__main__':
    server = HttpServer("", 8080, BaseHandler);
    server.startServer();