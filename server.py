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
        self.chat_history = []
        
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

    def add_connection(self, data, addr):
        username = data[1]
        if not (addr[0], addr[1]) in self.clients and not username in self.usernames and not username == "":
            self.clients.append((addr[0], addr[1]))
            self.usernames.append(username)
            
            # generate random color for user
            r = lambda: random.randint(0,255)
            random_color = str('#%02X%02X%02X' % (r(),r(),r()))
            join_message = ["join", "User " + username + " has joined the canvas with color: " + random_color + "\n",
                            "server", random_color, username]
            return join_message
        else:
            # send error message to client, username may be taken
            self.send_data(["ERROR"], addr[0], addr[1])
            return None
     
                        
    def accept_data(self, size=4096):
        while True:
            # Receive data from client
            data, addr = self.udp_socket.recvfrom(size)
            client_data = pickle.loads(data)

            # check if this client is trying to be added to our client list
            if client_data[0] == "username":
                # start_new_thread(self.add_username, (client_data, addr,))
                join_message = self.add_connection(client_data, addr)
                if join_message:
                    self.chat_history.append(["joing_chat", join_message[1]])
                    print(join_message[1]) # logging new client connected
                    self.send_data(join_message, addr[0], addr[1])

                    # send paint & chat history if there are older clients
                    if len(self.clients) > 1:
                        self.send_paint_history(addr[0], addr[1])
                        self.send_chat_history(addr[0], addr[1])
                    
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

    def send_paint_history(self, host, port, size=4096):
        for history in self.history:
            data = pickle.dumps(history)
            self.udp_socket.sendto(data, (host, port))

    def send_chat_history(self, host, port, size=4096):
        for chats in self.chat_history:
            data = pickle.dumps(chats)
            self.udp_socket.sendto(data, (host, port))

if __name__ == '__main__':
    server = Server()
    server.bind()
    server.accept_data()
