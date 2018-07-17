import socket
import sys
import paint
import pickle

class Client:
    def __init__(self):
        # self.tcp_socket = None
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

            # # TCP socket for establishing connection & chat
            # self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
            # self.tcp_socket.connect((host, (port + 1)))
            self.isClientConnected = True
            
        except socket.error as errorMessage:
            if errorMessage.errno == socket.errno.ECONNREFUSED:
                sys.stderr.write('Connection refused to {0} on port {1}'.format(host, port))
            else:
                sys.stderr.write('Error, unable to connect: {0}'.format(errorMessage))

    # def disconnect(self):
    #     if self.isClientConnected:
    #         self.udp_socket.close()
    #         self.isClientConnected = False

    def send_data(self, data):
        if self.isClientConnected:            
            list_data = pickle.dumps(data)
            self.udp_socket.sendto(list_data, (self.host,self.port))

    def receive_data(self, size=136):
        if not self.isClientConnected:
            return ""
        else:
            while True:
               data, addr = self.udp_socket.recvfrom(size)
               list_data = pickle.loads(data)
               if list_data:
                   print(list_data)
                   return list_data
               else:
                   return ""
            
    # def send(self, data):
    #     if self.isClientConnected:
    #         self.socket.send(data.encode())

            
    # def receive(self, size=4096):
    #     if not self.isClientConnected:
    #         return ""
    #     return self.socket.recv(size).decode('utf8')

client = Client()
client.connect('localhost', 10000)
if client.isClientConnected:
    paint = paint.Paint(client)
else:
    print("Client is not connected to the server, please check the server's status")
