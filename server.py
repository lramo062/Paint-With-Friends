import socket
import sys
from _thread import *
from multiprocessing import Process, Lock

# Function for handling connections. This will be used to create threads
def clientthread(conn):
    # infinite loop so threads don't exit
    while True:
        # conn.send(,).encode()
        # Receiving from client
        data = conn.recv(1024).decode()
        if not data: 
            break
        else:
            # create mutex lock
            mutex.acquire()
            try:
                print('client connected')
                conn.send(command_handler(data, paint_canvas).encode())
            finally: # release mutex
                mutex.release()
    # came out of loop
    conn.close()

HOST = 'localhost'
PORT = 10000

# create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# Bind socket to local host and port, print if fails
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
      
# Start listening on socket
s.listen(10)

# Initialize Flight Data
mutex = Lock()

# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    start_new_thread(clientthread,(conn,))

s.close()
