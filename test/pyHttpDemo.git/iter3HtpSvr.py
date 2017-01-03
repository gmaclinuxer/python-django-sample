

import socket, select;
from epollTools import parseHttpHeader, Request, handler;

svrScoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
svrScoket.setblocking(False);
svrScoket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
svrScoket.bind(("", 8080));
svrScoket.listen(1024);

epollSvr = select.epoll();
epollSvr.register(svrScoket.fileno(), select.EPOLLIN);

requests = {};
connections = {};

while True:
    events = epollSvr.poll(10);
    if not events:
        continue;

    #check all events
    for fileno, event in events:
        if fileno == svrScoket.fileno():
            #accept new scoket
            clientSocket, addr = svrScoket.accept();
            clientSocket.setblocking(False);
            epollSvr.register(clientSocket.fileno(), select.EPOLLIN);
            connections[clientSocket.fileno()] = clientSocket;

        elif event & select.EPOLLIN:
            #exsit client recvd
            if requests.has_key(fileno):
                request = requests[fileno];
            else:
                request = Request();
                requests[fileno] = request;
            request.rawInStr += connections[fileno].recv(1024);
            if parseHttpHeader(request):
                #parse success
                handler(request);
                epollSvr.modify(fileno, select.EPOLLOUT);
            else:
                #need to read data continue
                continue;
        elif event & select.EPOLLOUT:
            #write data to client
            if requests.has_key(fileno):
                request = requests[fileno];
                while len(request.rawOutStr) > 0:
                    sendBytes = connections[fileno].send(request.rawOutStr);
                    request.rawOutStr = request.rawOutStr[sendBytes:];
                del requests[fileno];
            epollSvr.unregister(fileno);
            connections[fileno].close();        
            del connections[fileno];

        elif event & select.EPOLLHUP:
            #client close connection
            epollSvr.unregister(fileno);
            connections[fileno].close();
            del requests[fileno];
            del connections[fileno];
