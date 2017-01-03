
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

#========================================

parten = {
    "/": index,
    "/iterator2": iterator2,
}

def handler(req):
    print req;
    #invalid connection
    if not req.has_key("URL"):
        return "";
    #404
    if not parten.has_key(req["URL"]):
        return "HTTP/1.1 404 Not Found\r\n\r\n 404 Error";
    try:
        return parten[req["URL"]](req);
    except:
        return "HTTP/1.1 500 Internal Server Error\r\n\r\n 500 Error";
