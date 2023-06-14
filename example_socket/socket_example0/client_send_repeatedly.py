#!/usr/bin/env python3
import socket
import time
# HOST = '10.0.1.9'
# HOST = '192.168.1.17'
HOST = '192.168.1.22'#esp32がつながるであろうアドレス
PORT = 8765

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))    
for i in range(100):        
    time.sleep(1)
    print(i)
    s.sendall(b'Hello, world')
    # data = s.recv(1024)
    
print('Received', repr(data))