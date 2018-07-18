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

        # Bind socket to local host and port, print if fails
        try:
            self.udp_socket.bind((self.HOST, self.PORT))
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
        username = data[0]

        # generate random color for user
        r = lambda: random.randint(0,255)
        random_color = str('#%02X%02X%02X' % (r(),r(),r()))
        
        if not username in self.usernames:
            self.usernames.append(username)
            chat_message = "User " + username + " has joined the canvas with color: " + random_color

            # send chat information
            print(chat_message)
            self.history.append([chat_message, "server", 0, 0, "chat"])
            
            # send random color & username for user
            color_data = [random_color, username, 0, 0, "color"]
            start_new_thread(self.send_data, (color_data, addr[0], addr[1],))
            start_new_thread(self.add_connection, (addr,))  # add client to client_list

        else:
            data = ["ERROR"]
            data = pickle.dumps(data)
            self.udp_socket.sendto(data, (addr[0], addr[1]))
                        
    def accept_data(self, size=4096):
        while True:
            # Receiving mouse data from client
            data, addr = self.udp_socket.recvfrom(size)
            cordinates = pickle.loads(data)
            if cordinates[4] == "username":
                start_new_thread(self.add_username, (cordinates, addr,))
            else:
                print(cordinates)
            
            # broadcast data out to all clients
            for host, port in self.clients:
                if cordinates[4] == "username":
                    continue
                else:
                     # used for logging information
                    self.history.append(cordinates)
                    start_new_thread(self.send_data, (cordinates, host, port,))

    def send_data(self, data, host, port, size=4096):
        data = pickle.dumps(data)
        self.udp_socket.sendto(data, (host, port))

if __name__ == '__main__':
    server = Server()
    server.bind()
    server.accept_data()

