import socket

def TCP_client(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connet(host, port)