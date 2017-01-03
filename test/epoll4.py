# coding=utf-8
# from __future__ import print_function
import socket, select, errno
import logging
import json
import sys


# ======================================================
# global settings
# ======================================================
DEBUG = False
back_log = 1024
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b''
# response += b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
# response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

# ======================================================
# log to file
# ======================================================
LOG_LEVEL = logging.INFO
if DEBUG:
    LOG_LEVEL = logging.DEBUG
def logto(filename, name=__name__, level=LOG_LEVEL):
    '''
    日志格式定义
    '''
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(levelname)-.3s [%(asctime)s.%(msecs)03d] %(threadName)-10s %(name)s:%(lineno)03d: %(message)s',
        '%Y%m%d-%H:%M:%S')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # show warning/error message direct
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger

# global logger
logger = logto('epoll.log')

# ======================================================
# overwrite buildin functions
# ======================================================
# try:
#     import __builtin__
# except ImportError:
#     import buildins as __build_in__
#
# if DEBUG is False:
#     def print(*args, **kwargs):
#         '''
#         custom print
#         '''
#         # __builtin__.print('custom print')
#         # return __builtin__.print(*args, **kwargs)
#         pass

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

# ======================================================
# epoll server
# ======================================================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 8888))
server_socket.listen(back_log)
# non-block mode
server_socket.setblocking(False)

# create epoll object
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLET)

print '''
    epoll           : %s
    server_socket   : %s
    server          : %s
    backlog         : %s
    debug           : %s
''' % (
    epoll.fileno(),
    server_socket.fileno(),
    '%s:%s' % server_socket.getsockname(),
    back_log,
    DEBUG
)

try:
    cons, reqs, resps, stats = {}, {}, {}, {}
    while True:
        events = epoll.poll(10)
        logger.debug('------epoll.poll------\n')
        for fileno, event in events:
            logger.debug('fd: %s, event: %s\n', fileno, trans_event(event))
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
                    logger.debug('EPOLLIN-accept: %s, EAGAIN: %s, client: %s' % (e.errno, errno.EAGAIN, fileno))
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
                            logger.warning('***recv_empty->close: %s***' % fileno)
                except socket.error as e:
                    if e.errno in [errno.EAGAIN]:
                        logger.debug('EPOLLIN: %s, EAGAIN: %s' % (e.errno, errno.EAGAIN))
                    else:
                        # socket.error: [Errno 107] Transport endpoint is not connected
                        try:
                            logger.warning('***%s->shutdown: %s***' % (fileno, e))
                            # epoll.modify(fileno, 0)
                            epoll.modify(fileno, select.EPOLLET)
                            cons[fileno].shutdown(socket.SHUT_RDWR)
                        except Exception as close_error:
                            logger.error('***%s->error: %s***' % (fileno, close_error))

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
                    logger.debug('EPOLLOUT: %s, EAGAIN: %s' % (e.errno, errno.EAGAIN))

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
                logger.debug('EPOLLHUP-%s' % fileno)
                update_stat(stats, fileno, 'recv_close')
                epoll.unregister(fileno)
                cons[fileno].close()
                del cons[fileno]
                # if fileno in reqs:
                #     del reqs[fileno]
except KeyboardInterrupt:
    logger.info('-' * 50 + '\n')
    logger.info(cons)
    logger.info(json.dumps(reqs, indent=2))
    logger.info(json.dumps(stats, indent=2))
    logger.info('\n' + '-' * 50)
finally:
    epoll.unregister(server_socket.fileno())
    epoll.close()
    server_socket.close()
