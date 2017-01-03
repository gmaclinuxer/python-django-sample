
import socket, select;
from multiprocessing import Pipe, reduction, Process;

class BaseHandler(object):

    parten = {};

    def __init__(self):
        pass

    def handle(self, req):
        #print req;
        #invalid connection
        if not req.has_key("URL"):
            return "";
        #404
        if not BaseHandler.parten.has_key(req["URL"]):
            req.rawOutStr = "HTTP/1.1 404 Not Found\r\n\r\n404 Error";
            return ;
        try:
            req.rawOutStr = BaseHandler.parten[req["URL"]](req);
        except:
            req.rawOutStr = "HTTP/1.1 500 Internal Server Error\r\n\r\n500 Error";


class Request(object):
    """
    http request
    """
    def __init__(self):
        self.rawInStr = "";#raw tcp input
        self.rawOutStr = ""; #raw tcp output
        self.dict = {}; #http request info

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
    @return: 
    -1 error header
    0 parse success
    1 incomplete header
    """
    delime = "\r\n";
    spliter = "\r\n\r\n";

    pos = req.rawInStr.find(spliter);
    if pos == -1:
        return 1;
    headStr = req.rawInStr[0:pos];
    dataStr = req.rawInStr[pos + len(spliter) :];
    headLines = headStr.split(delime);
    if len(headLines) == 0:
        return -1;

    first = headLines[0].split();
    if len(first) != 3:
        return -1;
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
    return 0;

class WorkerProcess(Process):
    """
    @brief: http worker, this is indivisual proccess.
    """
    def __init__(self, reqHandler, pipe):
        Process.__init__(self);
        self.connections = {};
        self.requests = {};
        self.workerEpoll = select.epoll();
        self.timeout = 1;
        self.reqHandler = reqHandler;
        self.childPipe = pipe;

    def close_client(self, client):
        self.workerEpoll.unregister(client);
        self.connections[client].close();
        del self.requests[client];
        del self.connections[client];

    def run(self):
        try:
            while True:
                #new client
                pipeNum = 0
                while self.childPipe.poll():
                    clientHandler = self.childPipe.recv();
                    clientFileno = reduction.rebuild_handle(clientHandler);
                    clientSocket = socket.fromfd(clientFileno, socket.AF_INET, socket.SOCK_STREAM);
                    clientSocket.setblocking(False);
                    self.workerEpoll.register(clientSocket.fileno(), select.EPOLLIN);
                    self.connections[clientSocket.fileno()] = clientSocket;
                    #control increasing client
                    pipeNum += 1;
                    if pipeNum > 10:
                        break;
                #new events
                events = self.workerEpoll.poll(0.001);
                if not events:
                    continue;
                for fd, event in events:
                    if event & select.EPOLLIN:
                        #recvd data from client
                        if self.requests.has_key(fd):
                            request = self.requests[fd];
                        else:
                            request = Request();
                            self.requests[fd] = request;

                        data = self.connections[fd].recv(1024);
                        if not data:
                            self.workerEpoll.modify(fd, 0);
                            self.connections[fd].shutdown(socket.SHUT_RDWR); 
                            continue;
                        request.rawInStr += data;
                        flag = parseHttpHeader(request)
                        if flag == 0:
                            handle = self.reqHandler();
                            handle.handle(request);
                            self.workerEpoll.modify(fd, select.EPOLLOUT);
                        elif flag == 1:
                            continue;
                        else:
                            self.workerEpoll.modify(fd, 0);
                            self.connections[fd].shutdown(socket.SHUT_RDWR); 
                    elif event & select.EPOLLOUT:
                        #write data to client
                        if self.requests.has_key(fd):
                            request = self.requests[fd];
                            while len(request.rawOutStr) > 0:
                                sendBytes = self.connections[fd].send(request.rawOutStr);
                                request.rawOutStr = request.rawOutStr[sendBytes:];
                        self.workerEpoll.modify(fd, 0);
                        self.connections[fd].shutdown(socket.SHUT_RDWR); 
                    elif event & select.EPOLLHUP:
                        #client close connection
                        self.close_client(fd);
        except Exception, e:
            print "stop worker...";
            self.childPipe.close();
            for fd in self.connections.keys():
                self.workerEpoll.unregister(fd);
                self.connections[fd].close();
                del self.connections[fd];
            print "end clean..."

class HttpServer(object):
    """
    epoll httpServer
    """
    def __init__(self, ip = "localhost", port = 8080, requestHandler = BaseHandler):
        """
        @brief: constructor
        """
        self.workers = [];
        self.workerPipe = [];
        self.ip = ip;
        self.port = port;
        self.svrSocket = None;
        self.timeout = 1;
        self.workerIndex = 0;
        self.requestHandler = requestHandler;
        self.dispatchEpoll = select.epoll();

    def __del__(self):
        print "HttpServer exist...bye...";

    def startServer(self, threadNum = 2):
        """
        @brief: start server with threadNum worker
        """
        #initial server socket
        self.svrSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.svrSocket.setblocking(False);
        self.svrSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
        self.svrSocket.bind((self.ip, self.port));
        self.dispatchEpoll.register(self.svrSocket.fileno(), select.EPOLLIN);
        
        #create worker
        if threadNum < 1:
            raise Exception("No worker define");
        for i in range(threadNum):
            print "Initial worker %d & worker pipe..." % i;
            parent, child = Pipe();
            wk = WorkerProcess(self.requestHandler, child);
            self.workers.append(wk);
            self.workerPipe.append(parent);
            wk.start();

        self.svrSocket.listen(1024);
        try:
            #set epoll event forever
            while True:
                events = self.dispatchEpoll.poll(10);
                if not events:
                    continue;
                for fd, event in events:
                    if fd == self.svrSocket.fileno():
                        clientSocket, addr = self.svrSocket.accept();
                        #print "HttpSvr: recvd connection: %s" % str(addr);
                        self.pushToWorker(clientSocket);
                    else:
                        self.dispatchEpoll.unregister(fd);
        except KeyboardInterrupt, e:
            print "Control + C, prepare close HttpServer...";
            self.stopServer();

    def stopServer(self):
        print "begin to stop accept server socket..."
        self.svrSocket.close();
        print "begin to stop worker...";
        for p in self.workers:
            p.terminate();

    def pushToWorker(self, client):
        clientHandler = reduction.reduce_handle(client.fileno());
        self.workerPipe[self.workerIndex].send(clientHandler);
        self.workerIndex = (self.workerIndex + 1) % len(self.workerPipe);