# coding=utf-8
import socket, select

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(1)
# non-block mode
server_socket.setblocking(0)

# create epoll object and register level trigger epoll fd
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN)

try:
    cons, reqs, resps = {}, {}, {}
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            # client connect event
            if fileno == server_socket.fileno():
                client_socket, address = server_socket.accept()
                # non-block mode
                client_socket.setblocking(0)
                # add client socket to epoll objects
                epoll.register(client_socket.fileno(), select.EPOLLIN)
                # store client socket
                cons[client_socket.fileno()] = client_socket
                reqs[client_socket.fileno()] = b''
                resps[client_socket.fileno()] = response
            elif event & select.EPOLLIN:
                reqs[fileno] += cons[fileno].recv(1024)
                # finish read
                if EOL1 in reqs[fileno] or EOL2 in reqs[fileno]:
                    # modify writable
                    epoll.modify(fileno, select.EPOLLOUT)
                    # ab -n 10000 http://localhost:8000
                    # comment next line when do ab test
                    # print '*' * 40 + '\n' + reqs[fileno].decode()[:-2]
            elif event & select.EPOLLOUT:
                bytes_written = cons[fileno].send(resps[fileno])
                resps[fileno] = resps[fileno][bytes_written:]
                # finish write
                if len(resps[fileno]) == 0:
                    # disable interest in further read or write events
                    epoll.modify(fileno, 0)
                    cons[fileno].shutdown(socket.SHUT_RDWR)
            elif event & select.EPOLLHUP:
                # client shutdown connection first
                epoll.unregister(fileno)
                cons[fileno].close()
                del cons[fileno]
finally:
    epoll.unregister(server_socket.fileno())
    epoll.close()
    server_socket.close()

