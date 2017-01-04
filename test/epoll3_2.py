# coding=utf-8
import socket, select

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
back_log = 1024
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8888))
server_socket.listen(back_log)
# non-block mode
server_socket.setblocking(0)
server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# create epoll object and register level trigger epoll fd
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN)

print ('''
    epoll           : %s
    server_socket   : %s
    server          : %s
    backlog         : %s
''' % (epoll.fileno(), server_socket.fileno(), '%s:%s' % server_socket.getsockname(), 1024))

try:
    cons, reqs, resps = {}, {}, {}
    while True:
        events = epoll.poll(10)
        if not events:
            print('empty event: %s' % events)
            continue
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
                recv_str = cons[fileno].recv(1024)
                if recv_str:
                    reqs[fileno] += recv_str
                else:
                    epoll.modify(fileno, 0)
                    cons[fileno].shutdown(socket.SHUT_RDWR)

                # finish read
                if EOL1 in reqs[fileno] or EOL2 in reqs[fileno]:
                    # modify writable
                    epoll.modify(fileno, select.EPOLLOUT)
                    cons[fileno].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
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
                    cons[fileno].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)
                    # epoll.unregister(fileno)
                    # cons[fileno].close()
                    # del cons[fileno]
                    cons[fileno].shutdown(socket.SHUT_RDWR)
            elif event & select.EPOLLHUP:
                # client shutdown connection first
                epoll.unregister(fileno)
                cons[fileno].close()
                del cons[fileno]
                # print 'fd: %s' % fileno
                del reqs[fileno]
except KeyboardInterrupt:
    print reqs
finally:
    epoll.unregister(server_socket.fileno())
    epoll.close()
    server_socket.close()

