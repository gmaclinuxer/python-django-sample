

class Request(object):
    """
    http request
    """
    def __init__(self):
        self.rawInStr = "";
        self.rawOutStr = "";
        self.dict = {};

    def __setitem__(self, key, value):
        self.dict[key] = value;

    def __getitem__(self, key):
        return self.dict.get(key, "");

    def __delitem__(self, key):
        del self.dict[key];

    def __str__(self):
        return str(self.dict);

    def has_key(self, key):
        return self.dict.has_key(key);


def parseParam(p):
    param = {};
    if not p:
        return param;
    for pair in p.split("&"):
        items = pair.split("=");
        param[items[0]] = items[1];
    return param;

def parseHttpHeader(req):
    """
    @parsm[in|out] req: request object
    """
    delime = "\r\n";
    spliter = "\r\n\r\n";

    pos = req.rawInStr.find(spliter);
    if pos == -1:
        return False;
    headStr = req.rawInStr[0:pos];
    dataStr = req.rawInStr[pos + len(spliter) :];
    headLines = headStr.split(delime);
    if len(headLines) == 0:
        return False;

    first = headLines[0].split();
    if len(first) != 3:
        return False;
    req["METHOD"] = first[0];
    req["URL"] = first[1];
    req["VERSION"] = first[2];
    for line in headLines[1:]:
        items = line.split(": ");
        req[items[0]] = items[1];
    if req["METHOD"] == "GET":
        ps = req["URL"].find("?");
        if ps != -1:
            req["param"] = parseParam(req["URL"][ps + 1 :]);
            req["URL"] = req["URL"][0:ps];
    else:
        req["param"] = parseParam(dataStr);
    return True;

#==============================================================


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
    #print req;
    #invalid connection
    if not req.has_key("URL"):
        return "";
    #404
    if not parten.has_key(req["URL"]):
        req.rawOutStr = "HTTP/1.1 404 Not Found\r\n\r\n404 Error";
        return ;
    try:
        req.rawOutStr = parten[req["URL"]](req);
    except:
        req.rawOutStr = "HTTP/1.1 500 Internal Server Error\r\n\r\n500 Error";
