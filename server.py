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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind socket to local host and port, print if fails
        try:
            self.socket.bind((self.HOST, self.PORT))
        except socket.error as msg:
            print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def listen(self):
        # Start listening on socket
        self.socket.listen(10)
        # now keep talking with the client
        while True:
            # wait to accept a connection - blocking call
            (conn, addr) = self.socket.accept()
            self.clients.append((conn, addr))
            self.print_connections()
            start_new_thread(self.clientthread, (conn,))
            
    def print_connections(self):
        for conn, addr in self.clients:
            print('Connected with ' + addr[0] + ':' + str(addr[1]))
    
    def clientthread(self, conn):
        # infinite loop so threads don't exit
        while True:
            # Receiving from client
            cordinates = pickle.loads(conn.recv(4096))
            if cordinates:
                # create mutex lock
                self.mutex.acquire()
                try: 
                    print(cordinates)
                    list_data = pickle.dumps(cordinates)
                    for conn, addr in self.clients:
                        conn.sendall(list_data)
                finally:
                    self.mutex.release()
            else:
                break
        # come out of loop
        conn.close()
        
server = Server()
server.bind()
server.listen()
