# coding=utf-8
from __future__ import print_function
import socket, select, errno
import datetime

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8888))
server_socket.listen(1)
# non-block mode
server_socket.setblocking(0)

# create epoll object
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLET)

print ('''
    epoll           : %s
    server_socket   : %s
    server          : %s
''' % (epoll.fileno(), server_socket.fileno(), '%s:%s' % server_socket.getsockname()))


def trans_event(event_no):
    return {
        select.EPOLLIN: 'readable',
        select.EPOLLOUT: 'writable',
        select.EPOLLHUP: 'disconnect'
    }.get(event_no)

# ======================================================
# overwrite buildin functions
# ======================================================
try:
    import __builtin__
except ImportError:
    import buildins as __build_in__

DEBUG = True
if DEBUG is False:
    def print(*args, **kwargs):
        '''
        custom print
        '''
        # __builtin__.print('custom print')
        # return __builtin__.print(*args, **kwargs)
        pass
try:
    cons, reqs, resps = {}, {}, {}
    cnt = 0
    while True:
        events = epoll.poll()
        for fileno, event in events:
            # print('%s: fd: %s, event: %s' % (datetime.datetime.now(), fileno, trans_event(event)))
            # client connect event
            if fileno == server_socket.fileno():
                try:
                    while True:
                        client_socket, address = server_socket.accept()
                        # non-block mode
                        client_socket.setblocking(0)
                        # add client socket to epoll objects
                        epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLET)
                        # store client socket
                        cons[client_socket.fileno()] = client_socket
                        reqs[client_socket.fileno()] = b''
                        resps[client_socket.fileno()] = response
                except socket.error as e:
                    # print('%s: EPOLLIN-accept: %s, EAGAIN: %s, client: %s' % (datetime.datetime.now(), e.errno, errno.EAGAIN, client_socket.fileno()))
                    pass
            elif event & select.EPOLLIN:
                try:
                    while True:
                        recv_str = cons[fileno].recv(1024)
                        # print recv_str, fileno
                        reqs[fileno] += recv_str
                except socket.error as e:
                    print('%s: EPOLLIN: %s, EAGAIN: %s' % (datetime.datetime.now(), e.errno, errno.EAGAIN))
                    pass

                # finish read
                if EOL1 in reqs[fileno] or EOL2 in reqs[fileno]:
                    # modify writable
                    epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                    # print '*' * 40 + '\n' + reqs[fileno].decode()[:-2]

            elif event & select.EPOLLOUT:
                try:
                    while len(resps[fileno]) > 0:
                        bytes_written = cons[fileno].send(resps[fileno])
                        resps[fileno] = resps[fileno][bytes_written:]
                except socket.error as e:
                    # print('%s: EPOLLOUT: %s, EAGAIN: %s' % (datetime.datetime.now(), e.errno, errno.EAGAIN))
                    pass

                # finish write
                if len(resps[fileno]) == 0:
                    # disable interest in further read or write events
                    epoll.modify(fileno, select.EPOLLET)
                    cons[fileno].shutdown(socket.SHUT_RDWR)

            elif event & select.EPOLLHUP:
                # client shutdown connection first
                # print('%s: EPOLLHUP-%s' % (datetime.datetime.now(), fileno))
                epoll.unregister(fileno)
                cons[fileno].close()
                del cons[fileno]
finally:
    epoll.unregister(server_socket.fileno())
    epoll.close()
    server_socket.close()
