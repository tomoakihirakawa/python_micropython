#!/usr/bin/env python3
import socket
# HOST = '10.0.1.9'
# HOST = '192.168.1.17'
# HOST = '192.168.1.22'#esp32がつながるであろうアドレス
# PORT = 8765

HOST = "127.0.0.1"
PORT = 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)
    
print('Received', repr(data))