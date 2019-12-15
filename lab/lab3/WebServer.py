from socket import *
import sys
port = int(sys.argv[1])

print(port)

server = socket(AF_INET, SOCK_STREAM)

server.bind(('127.0.0.1',port))

server.listen(1)

while True:
	client, addr = server.accept()
	try:
		message = client.recv(1024).decode()
		a = message.split()[1]
		file_1 = open(a[1:],'rb')
		
		line = file_1.read()
		client.send(b"HTTP/1.1 200 OK\r\n\r\n")
		client.send(line)
		client.close()
	except IOError:
		client.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
		client.send(b"404 Not Found")
		client.close()


