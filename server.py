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

    def add_username(self, data, addr):
        username = data[0]

        # generate random color for user
        r = lambda: random.randint(0,255)
        random_color = str('#%02X%02X%02X' % (r(),r(),r()))
        
        if not username == "" and not username in self.usernames:
            self.usernames.append(username)
            join_message = ["User " + username + " has joined the canvas with color: " + random_color + "\n",
                            "server", random_color, username, "join"]
            return join_message
        else:
            # send error message to client, username may be taken
            self.send_data(["ERROR"], addr[0], addr[1])
            return (None, None)
                        
    def accept_data(self, size=4096):
        while True:
            # Receive data from client
            data, addr = self.udp_socket.recvfrom(size)
            client_data = pickle.loads(data)

            # check if this client is trying to be added to our client list
            if client_data[4] == "username":
                # start_new_thread(self.add_username, (client_data, addr,))
                join_message = self.add_username(client_data, addr)
                if join_message:
                    self.history.append([join_message[0], 0, 0, 0, "join_chat"])
                    print(join_message[0]) # logging new client connected
                    # add the new client to our client list
                    # and send them the history of all data
                    start_new_thread(self.add_connection, (addr,))
                    self.mutex.acquire()
                    start_new_thread(self.send_data, (join_message, addr[0], addr[1],))
                    self.mutex.release()
                    start_new_thread(self.send_data, (self.history, addr[0], addr[1],))
                    
            else:
                print(client_data)
                # broadcast data out to all clients
                for host, port in self.clients:
                    # used for logging information
                    self.history.append(client_data)
                    if not (host, port) == (addr[0], addr[1]):
                        start_new_thread(self.send_data, (client_data, host, port,))

    def send_data(self, data, host, port, size=4096):
        data = pickle.dumps(data)
        self.udp_socket.sendto(data, (host, port))

if __name__ == '__main__':
    server = Server()
    server.bind()
    server.accept_data()
