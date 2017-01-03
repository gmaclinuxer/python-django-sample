
import json, socket;
from asyncore import dispatcher;
from asynchat import async_chat;

def parseParam(p):
    param = {};
    if not p:
        return param;
    for pair in p.split("&"):
        items = pair.split("=");
        param[items[0]] = items[1];
    return param;

class HttpHandler(async_chat):
    """
    @brief: http request handler
    """
    METHODLIST = ["GET", "POST"];
    parten = {};
    def __init__(self, server, socket):
        async_chat.__init__(self, socket);
        self.server = server;
        self.rawInStr = "";
        self.rawOutStr = "";
        self.request = {};
        self.set_terminator("\r\n\r\n");
        self.found_terminator = self.handle_http_header;

    def collect_incoming_data(self, data):
        self.rawInStr += data;
        
    def handle_http_header(self):
        """
        @brief: parse http header when find out '\r\n\r\n'
        """
        requestLines = self.rawInStr.split("\r\n");
        if len(requestLines) < 1:
            self.close();
            return ;
        firstLine = requestLines[0].split();
        if len(firstLine) != 3:
            self.close();
            return;
        method, url, version = firstLine;
        if method not in self.METHODLIST:
            self.close();
            return;

        self.request["METHOD"] = method;
        self.request["VERSION"] = version;
        self.request["param"] = {};
        self.request["URL"] = url;
        
        if method == "GET":
            #paras GET params
            index = url.find("?");
            if index != -1:
                self.request["param"] = parseParam(url[index + 1:]);
                self.request["URL"] = url[:index];
                
        #parse other header item
        for line in requestLines[1:]:
            key, value = line.split(": ");
            self.request[key] = value;
        
        if method != "GET":
            #read request body
            if not self.request.has_key("Content-Length"):
                self.close();
                return;
            #still need to read content-Length string for body
            self.found_terminator = self.handle_http_body;
            self.rawInStr = "";
            self.set_terminator(int(self.request["Content-Length"]));
            return ;
        else:
            #handle get request
            self.handle_request();

    def handle_http_body(self):
        """
        @brief: call back when read http request body
        """
        if len(self.rawInStr) != self.request["Content-Length"]:
            self.close();
            return;
        self.request["param"] = parseParam(self.rawInStr);
        self.handle_request();

    def handle_request(self):
        #404
        if not HttpHandler.parten.has_key(self.request["URL"]):
            self.push("HTTP/1.1 404 Not Found\r\n\r\n404 Error");
            self.close();
            return ;
        try:
            self.push(HttpHandler.parten[self.request["URL"]](self.request));
        except:
            self.push("HTTP/1.1 500 Internal Server Error\r\n\r\n500 Error");
        self.close();
        return;

class AsyncHttpServer(dispatcher):
    """
    """
    def __init__(self, port):
        dispatcher.__init__(self);
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM);
        self.bind(("", port));
        self.listen(1024);

    def handle_accept(self):
        conn, addr = self.accept();
        HttpHandler(self, conn);
