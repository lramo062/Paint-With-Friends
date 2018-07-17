import socket
import sys
import pickle
import random
from _thread import *
from multiprocessing import Process, Lock

class Server:
    def __init__(self):
        self.HOST = 'localhost'
        self.PORT = 10000
        self.socket = None
        self.clients = []
        self.usernames = []
        self.mutex = Lock()
        self.history = []
        
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

            # sending draw history to new client
            for data in self.history:
                self.send_data(data, addr[0], addr[1])

    def add_username(self, data, addr):
        # generate random color for user
        r = lambda: random.randint(0,255)
        random_color = str('#%02X%02X%02X' % (r(),r(),r()))
        
        if not data[0] in self.usernames:
            self.usernames.append(data[0])
            print("User: " + data[0] + " has joined the canvas with color: " + random_color)
        
            # send random color & username for user
            color_data = [random_color, data[0], 0, 0, "color"]
            color_data = pickle.dumps(color_data)
            self.udp_socket.sendto(color_data, (addr[0], addr[1]))
            self.add_connection(addr) # add client to client_list

        else:
            data = ["ERROR"]
            data = pickle.dumps(data)
            self.udp_socket.sendto(data, (addr[0], addr[1]))
            
    # def accept_connections(self):
    #     while True:
    #         # add connected clients to client list
    #         conn, tcp_addr = self.tcp_socket.accept()
    #         self.add_connection(tcp_addr)
    #         start_new_thread(self.accept_data, ())
            
    def accept_data(self, size=4096):
        while True:
            # Receiving mouse data from client
            data, addr = self.udp_socket.recvfrom(size)
            cordinates = pickle.loads(data)
            if cordinates[4] == "username":
                self.add_username(cordinates, addr)    
            else:
                print(cordinates)
            
            # broadcast data out to all clients
            for host, port in self.clients:
                if cordinates[4] == "username":
                    continue
                else:
                     # used for logging information
                    self.history.append(cordinates)
                    self.send_data(cordinates, host, port)

    def send_data(self, data, host, port, size=4096):
        data = pickle.dumps(data)
        self.udp_socket.sendto(data, (host, port))

server = Server()
server.bind()
# server.accept_connections()
server.accept_data()

