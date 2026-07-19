import socket,sys
try:
    s=socket.create_connection(('127.0.0.1',5000),2)
    print('CONNECTED')
    s.close()
except Exception as e:
    print('ERR',e)
    sys.exit(1)
