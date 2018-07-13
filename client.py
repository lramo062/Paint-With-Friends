import socket
import sys
import paint
import pickle

class Client:
    def __init__(self):
        self.socket = None
        self.isClientConnected = False

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect((host, port))
            self.isClientConnected = True
        except socket.error as errorMessage:
            if errorMessage.errno == socket.errno.ECONNREFUSED:
                sys.stderr.write('Connection refused to {0} on port {1}'.format(host, port))
            else:
                sys.stderr.write('Error, unable to connect: {0}'.format(errorMessage))

    def disconnect(self):
        if self.isClientConnected:
            self.socket.close()
            self.isClientConnected = False

    def send_list(self, data):
        if self.isClientConnected:
            list_data = pickle.dumps(data)
            self.socket.send(list_data)

    def send(self, data):
        if self.isClientConnected:
            self.socket.send(data.encode())

            
    def receive(self, size=4096):
        if not self.isClientConnected:
            return ""
        return self.socket.recv(size).decode('utf8')

    def receive_list(self, size=4096):
        if not self.isClientConnected:
            return ""
        return pickle.loads(self.socket.recv(size))


client = Client()
client.connect('localhost', 10000)
if client.isClientConnected:
    paint = paint.Paint(client)
else:
    print("Client is not connected to the server, please check the server's status")
