# coding=utf-8
import socket

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(1)

try:
    while True:
        client_socket, address = server_socket.accept()
        request = b''
        while EOL1 not in request and EOL2 not in request:
            request += client_socket.recv(1024)

        print '*' * 40 + '\n' + request.decode()[:-2]
        client_socket.send(response)
        client_socket.close()
finally:
    server_socket.close()

