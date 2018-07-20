import socket
import sys
import paint
import pickle

class Client:
    def __init__(self):
        self.udp_socket = None
        self.host = None
        self.port = None
        self.isClientConnected = False
        
    def connect(self, host, port):
        self.host = host
        self.port = port
        try:
            # UDP socket for sending/receiving drawing data
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
            self.udp_socket.connect((host, port))
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
            list_data = pickle.dumps(data)
            self.udp_socket.sendto(list_data, (self.host,self.port))

    def receive_data(self, size=4096):
        if not self.isClientConnected:
            return ""
        else:
            while True:
               data, addr = self.udp_socket.recvfrom(size)
               list_data = pickle.loads(data)
               if list_data:
                   return list_data
               else:
                   return ""

if __name__ == '__main__':
    client = Client()
    client.connect('127.0.0.1', 10000)
    paint = paint.Paint(client)
