import socket
import sys
import pickle
from _thread import *
from multiprocessing import Process, Lock


class Server:
    def __init__(self):
        self.HOST = 'localhost'
        self.PORT = 10000
        self.socket = None
        self.clients = []
        self.mutex = Lock()
        
    def disconnect(self):
        self.socket.close()
    
    def bind(self):
        # UDP socket for sending/receiving drawing data
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # # TCP socket for establishing connection & chat
        # self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind socket to local host and port, print if fails
        try:
            self.udp_socket.bind((self.HOST, self.PORT))
            # self.tcp_socket.bind((self.HOST, (self.PORT + 1)))
            # self.tcp_socket.listen(10)
        except socket.error as msg:
            print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def add_connection(self, addr):
        if not (addr[0], addr[1]) in self.clients:
            self.clients.append((addr[0], addr[1]))
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
                
    # def accept_connections(self):
    #     while True:
    #         # add connected clients to client list
    #         conn, tcp_addr = self.tcp_socket.accept()
    #         self.add_connection(tcp_addr)
    #         start_new_thread(self.accept_data, ())
            
    def accept_data(self, size=136):
        while True:
            # Receiving mouse data from client
            data, addr = self.udp_socket.recvfrom(size)
            self.add_connection(addr)
            cordinates = pickle.loads(data)
            print(cordinates)
            
            list_data = pickle.dumps(cordinates)
            for host, port in self.clients:
                self.mutex.acquire()
                self.udp_socket.sendto(data, (host, port))
                self.mutex.release()
        
server = Server()
server.bind()
# server.accept_connections()
server.accept_data()

