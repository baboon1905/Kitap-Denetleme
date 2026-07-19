import socket
s=socket.socket()
s.settimeout(5)
s.connect(('127.0.0.1',5000))
req=b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
s.sendall(req)
try:
    data=s.recv(4096)
    print(data.decode('utf-8', errors='replace'))
except Exception as e:
    print('ERR', e)
s.close()
