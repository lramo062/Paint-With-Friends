import socket
import sys
import paint
import json

class Client:
    def __init__(self):
        self.udp_socket = None
        self.HOST = "localhost"
        self.PORT = 4000
        self.TCP_PORT = 4001
        self.isClientConnected = False
        self.history = None
        
    def connect(self):
        try:
            # UDP socket for sending/receiving drawing data
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)            
            self.udp_socket.connect((self.HOST, self.PORT))

            # TCP socket for receiving history
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.HOST, self.TCP_PORT))
            self.isClientConnected = True
            self.receive_history()
            self.tcp_socket.close()
            
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
               if data:
                   return json.loads(data)
                                  
    def receive_history(self, size=1073741824):
        if not self.isClientConnected:
            return ""
        else:
            while True:
                data = self.tcp_socket.recv(size)             
                if data:
                    self.history = json.loads(data)
                else:
                    break

if __name__ == '__main__':
    client = Client()
    client.connect()
    paint = paint.Paint(client)
