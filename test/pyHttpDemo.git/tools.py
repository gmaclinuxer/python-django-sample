

def parseParam(p):
    param = {};
    if not p:
        return param;
    for pair in p.split("&"):
        items = pair.split("=");
        param[items[0]] = items[1];
    return param;

def parseHttpHeader(readBuf):
    delime = "\r\n";
    spliter = "\r\n\r\n";

    pos = readBuf.find(spliter);
    request = {};
    if pos == -1:
        return request;
    headStr = readBuf[0:pos];
    dataStr = readBuf[pos + len(spliter) :];
    headLines = headStr.split(delime);
    if len(headLines) == 0:
        return request;

    first = headLines[0].split();
    if len(first) != 3:
        return request;
    request["METHOD"] = first[0];
    request["URL"] = first[1];
    request["VERSION"] = first[2];
    for line in headLines[1:]:
        items = line.split(": ");
        request[items[0]] = items[1];
    if request["METHOD"] == "GET":
        ps = request["URL"].find("?");
        if ps != -1:
            request["param"] = parseParam(request["URL"][ps + 1 :]);
            request["URL"] = request["URL"][0:ps];
    else:
        request["param"] = parseParam(dataStr);
    return request;

