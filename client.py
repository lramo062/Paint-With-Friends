import socket
import sys
import paint
import json

class Client:
    def __init__(self):
        self.udp_socket = None
        self.HOST = "localhost"
        self.PORT = 10000
        self.isClientConnected = False
        
    def connect(self):
        try:
            # UDP socket for sending/receiving drawing data
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
            self.udp_socket.connect((self.HOST, self.PORT))
            self.isClientConnected = True
            
        except socket.error as errorMessage:
            if errorMessage.errno == socket.errno.ECONNREFUSED:
                sys.stderr.write('Connection refused to {0} on port {1}'.format(host, port))
            else:
                sys.stderr.write('Error, unable to connect: {0}'.format(errorMessage))
                
    def disconnect(self):
        if self.isClientConnected:
            self.udp_socket.close()
            self.isClientConnected = False

    def send_data(self, data):
        if self.isClientConnected:
            self.udp_socket.sendto(json.dumps(data).encode(), (self.HOST, self.PORT))

    def receive_data(self, size=1073741824):
        if not self.isClientConnected:
            return ""
        else:
            while True:
               data, addr = self.udp_socket.recvfrom(size)
               list_data = json.loads(data)
               if list_data:
                   return list_data
               else:
                   return ""

if __name__ == '__main__':
    client = Client()
    client.connect()
    paint = paint.Paint(client)
