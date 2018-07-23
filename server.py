import socket
import sys
import json
import random
from _thread import *

class Server:
    def __init__(self):
        self.HOST = 'localhost'
        self.UDP_PORT = 4000
        self.TCP_PORT = 4001
        self.udp_socket = None
        self.tcp_socket = None
        self.clients = []
        self.usernames = []
        self.history = []
    
    def bind(self):
        # UDP/TCP socket for sending/receiving drawing data/ history
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind socket to local host and port, print if fails
        try:
            self.udp_socket.bind((self.HOST, self.UDP_PORT))
            self.tcp_socket.bind((self.HOST, self.TCP_PORT))
            self.tcp_socket.listen(10)
        except socket.error as msg:
            print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def generate_random_color(self):
         r = lambda: random.randint(0,255)
         return str('#%02X%02X%02X' % (r(),r(),r()))
            
    def add_connection(self, data, addr):
        username = data[1]
        if not (addr[0], addr[1]) in self.clients and not username in self.usernames and not username == "":
            self.clients.append((addr[0], addr[1]))
            self.usernames.append(username)
            # generate random color for user & send back confirmation
            random_color = self.generate_random_color()
            join_message = ["join_chat",
                            "User " + username + " has joined the canvas with color: " + random_color + "\n",
                            "server", random_color, username]
            self.send_data(join_message, addr[0], addr[1])
            return join_message
        else:
            # send error message to client, username may be taken
            self.send_data(["ERROR"], addr[0], addr[1])
            return None
                        
    def accept_data(self, size=4096):
        while True:
            # Receive data from client
            data, addr = self.udp_socket.recvfrom(size)
            client_data = json.loads(data)
            print(client_data) # log data

            # check if this client is trying to be added to our client list
            if client_data[0] == "username":                
                join_message = self.add_connection(client_data, addr)
                if join_message:                
                    self.history.append(["join_chat", join_message[1], join_message[4]])
                    start_new_thread(self.broadcast_data, (client_data,))
            else:
                self.history.append(client_data)
                # broadcast data out to all clients
                start_new_thread(self.broadcast_data, (client_data,))

    def accept_tcp_connection(self):
        while True:
            conn, tcp_addr = self.tcp_socket.accept()
            if len(self.history) > 1:
                conn.send(json.dumps(self.history).encode())
            conn.close()
        
    def send_data(self, data, host, port):
        self.udp_socket.sendto(json.dumps(data).encode(), (host, port))

    def broadcast_data(self, data):
        for host, port in self.clients:
            self.send_data(data, host, port)

if __name__ == '__main__':
    server = Server()
    server.bind()
    start_new_thread(server.accept_tcp_connection, ())
    server.accept_data()
