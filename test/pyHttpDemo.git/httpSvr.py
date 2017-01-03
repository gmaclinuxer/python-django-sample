
import socket;

svrScoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
svrScoket.bind(("localhost", 8080));
svrScoket.listen(10);

while True:
    con, addr = svrScoket.accept();
    buf = con.recv(1024);
    print addr;
    print buf;
    con.send("Hello, this is jimwu.");
    con.close();