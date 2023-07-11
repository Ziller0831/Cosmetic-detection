import socket

def TCP_client(host, port, message_ost):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message_ost.encode())
        data = s.recv(1024)
    return data