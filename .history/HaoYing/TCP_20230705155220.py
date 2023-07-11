import socket

def TCP_client(Host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connet(host, Port)