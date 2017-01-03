# coding=utf-8
from __future__ import print_function
import socket, select, errno
import datetime
import logging
import json
import sys

def logto(filename, name=__name__, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(levelname)-.3s [%(asctime)s.%(msecs)03d] %(threadName)-10s %(name)s:%(lineno)03d: %(message)s',
        '%Y%m%d-%H:%M:%S')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if level == logging.DEBUG:
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
    return logger

# 文件日志
logger = logto('epoll.log')

DEBUG = False
back_log = 1024
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b''
# response += b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
# response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 8888))
server_socket.listen(back_log)
# non-block mode
server_socket.setblocking(False)

# create epoll object
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLET)

print('''
    epoll           : %s
    server_socket   : %s
    server          : %s
    backlog         : %s
    debug           : %s
''' % (epoll.fileno(), server_socket.fileno(), '%s:%s' % server_socket.getsockname(), back_log, DEBUG))

# ======================================================
# overwrite buildin functions
# ======================================================
try:
    import __builtin__
except ImportError:
    import buildins as __build_in__

if DEBUG is False:
    def print(*args, **kwargs):
        '''
        custom print
        '''
        # __builtin__.print('custom print')
        # return __builtin__.print(*args, **kwargs)
        pass



# ======================================================
# tools
# ======================================================
def trans_event(event_no):
    return {
        select.EPOLLIN: 'readable',
        select.EPOLLOUT: 'writable',
        select.EPOLLHUP: 'disconnect'
    }.get(event_no)

def update_stat(stats, fd, k, v=None):
    '''
    epoll状态统计
    '''
    # print(stats)
    socket_file = stats[fd]
    if v is None:
        socket_file[k] = socket_file[k] + 1
    else:
        socket_file[k] = v

STAT_DEFAULT = {'epoll_in': 0, 'epoll_out': 0, 'send_close': 0, 'recv_close': 0, 'recv_empty': 0}
# ======================================================
# epoll server
# ======================================================
try:
    cons, reqs, resps, stats = {}, {}, {}, {}
    cnt = 0
    while True:
        events = epoll.poll(10)
        # print('------epoll.poll------\r\n')
        for fileno, event in events:
            # print('%s: fd: %s, event: %s' % (datetime.datetime.now(), fileno, trans_event(event)))
            # client connect event
            if fileno == server_socket.fileno():
                try:
                    while True:
                        # print('------accept entry------\r\n')
                        client_socket, address = server_socket.accept()
                        # non-block mode
                        client_socket.setblocking(False)
                        # add client socket to epoll objects
                        epoll.register(client_socket.fileno(), select.EPOLLIN | select.EPOLLET)
                        # store client socket
                        cons[client_socket.fileno()] = client_socket
                        reqs[client_socket.fileno()] = b''
                        resps[client_socket.fileno()] = response
                        stats[client_socket.fileno()] = {
                            'epoll_in': 0, 'epoll_out': 0, 'send_close': 0, 'recv_close': 0, 'recv_empty': 0
                        }
                except socket.error as e:
                    print('%s: EPOLLIN-accept: %s, EAGAIN: %s, client: %s' % (
                        datetime.datetime.now(), e.errno, errno.EAGAIN, fileno))
                    pass
            elif event & select.EPOLLIN:
                try:
                    while True:
                        recv_str = cons[fileno].recv(1024)
                        # ps -ef|grep 'epoll4'|grep -v grep|awk '{print $2}'|xargs strace -p
                        # recvfrom(264, "", 1024, 0, NULL, NULL)  = 0
                        # recvfrom(264, "", 1024, 0, NULL, NULL)  = 0
                        # ...
                        if recv_str:
                            update_stat(stats, fileno, 'epoll_in')
                            reqs[fileno] += recv_str
                        else:
                            # ab -n 10000 -c 800 http://localhost:8888/ many CLOSE_WAIT bug test
                            update_stat(stats, fileno, 'recv_empty')
                            # epoll.modify(fileno, 0)
                            epoll.modify(fileno, select.EPOLLET)
                            cons[fileno].shutdown(socket.SHUT_RDWR)
                            logger.info('%s: ***recv_empty->shutdown: %s***' % (datetime.datetime.now(), fileno))
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
                        update_stat(stats, fileno, 'epoll_out')
                except socket.error as e:
                    print('%s: EPOLLOUT: %s, EAGAIN: %s' % (datetime.datetime.now(), e.errno, errno.EAGAIN))
                    pass

                # finish write
                if len(resps[fileno]) == 0:
                    # disable interest in further read or write events
                    # server close connection
                    epoll.modify(fileno, select.EPOLLET)
                    cons[fileno].shutdown(socket.SHUT_RDWR)
                    # if fileno in reqs:
                    #     del reqs[fileno]
                    # epoll.unregister(fileno)
                    # cons[fileno].close()
                    # del cons[fileno]
                    update_stat(stats, fileno, 'send_close')

            elif event & select.EPOLLHUP:
                # client close connection
                print('%s: EPOLLHUP-%s' % (datetime.datetime.now(), fileno))
                update_stat(stats, fileno, 'recv_close')
                epoll.unregister(fileno)
                cons[fileno].close()
                del cons[fileno]
                # if fileno in reqs:
                #     del reqs[fileno]
except KeyboardInterrupt:
    logger.info('-'*50 + '\n')
    logger.info(cons)
    logger.info(json.dumps(reqs, indent=2))
    logger.info(json.dumps(stats, indent=2))
    logger.info('\n' + '-'*50)
finally:
    epoll.unregister(server_socket.fileno())
    epoll.close()
    server_socket.close()
