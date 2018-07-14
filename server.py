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
        # create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind socket to local host and port, print if fails
        try:
            self.socket.bind((self.HOST, self.PORT))
        except socket.error as msg:
            print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    # def accept_data(self):
    #     # now keep talking with the client
    #     # (conn, addr) = self.socket.accept()
    #     # self.clients.append((conn, addr))
    #     # self.print_connections()
    #     start_new_thread(self.clientthread, ())
    #     print("After thread")
        

    def add_connection(self, addr):
        self.clients.append((addr[0], addr[1]))
    
    def print_connections(self):
        for host, port in self.clients:
            print('Connected with ' + host + ':' + str(port))
    
    def accept_data(self):
        # infinite loop so threads don't exit
        while True:
            # Receiving from client
            data, addr = self.socket.recvfrom(4096)
            self.add_connection(addr)
            cordinates = pickle.loads(data)
            print(cordinates)
            if not cordinates:
                break
            
            else:
                list_data = pickle.dumps(cordinates)
                for host, port in self.clients:
                    self.socket.sendto(data, (host, port))
                    
    #             start_new_thread(self.send_data, (list_data,))

    # def send_data(self, data):
    #     # self.mutex.acquire()  
    #     # self.mutex.release()

server = Server()
server.bind()
server.accept_data()

