
import socket;
from tools import parseHttpHeader;
from iterator2 import *;

svrScoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
svrScoket.bind(("localhost", 8080));
svrScoket.listen(10);

while True:
    con, addr = svrScoket.accept();
    buf = con.recv(1024);
    request = parseHttpHeader(buf);
    request["client"] = addr[0];
    request["client_port"] = addr[1];
    response = handler(request);
    con.send(response);
    con.close();