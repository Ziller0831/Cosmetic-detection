import socket

def Client(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(message.encode('utf-8'))
        data = s.recv(1024)
    return data