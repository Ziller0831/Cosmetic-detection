import socket

class TCP:
    def __init__(self):
        ServerHost = '0.0.0.0'
        ServerPort = 8080
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ServerHost, ServerPort))

    def sendMessages(self, message):
        self.s.send(message.encode('utf8'))