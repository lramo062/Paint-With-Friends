import socket
import paint

# define socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define server
server = 'localhost'
port = 10000

s.connect((server,port))

# paint_canvas = s.recv(4096).decode()
paint_canvas = paint.Paint()

#while True:
    
# s.close()
