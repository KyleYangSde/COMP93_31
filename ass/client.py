import time
import threading
import sys
from socket import *
import pickle



def client_recv(TCP_Socket3):
    print(1)
    while True:
        received = TCP_Socket3.recv(2048)
        received = received.decode()
        print(received)

def client_send(TCP_Socket3):
    message = input()
    TCP_Socket3.send(message.encode())


def server_recv(serverSocket):
    while True:
        connectionSocket, addr = serverSocket.accept()#current connection
        received = connectionSocket.recv(2048)
        received = received.decode()
        print(received)


def server_send(serverSocket):
    while True:
        connectionSocket, addr = serverSocket.accept()#current connection
        message = input()
        connectionSocket.send(message.encode())
        

def throw():
    try:
        raise Exception
    except Exception:
        sys.exit()
        
def receiveFunction():

    global TCP_Socket
    global auth
    while True:
        try:
            received = TCP_Socket.recv(2048)
            received = received.decode()
            print(received)
        except OSError:
            pass
        if 'Welcome' in received:
            auth = True
        if 'timeout' in received:
            TCP_Socket.close()
            sys.exit()
        if 'server' in received:
            while True:
            #setup serversocket
                splitt  = received.split(':')
                serverSocket = socket(AF_INET, SOCK_STREAM)
                serverSocket.bind((serverName, int(splitt[1])))
                serverSocket.listen(0)
                time.sleep(5)
                #set up client
                TCP_Socket3 = socket(AF_INET, SOCK_STREAM)
                TCP_Socket3.connect((serverName, int(splitt[1])))
                return_message = input()
                TCP_Socket3.send(return_message.encode())
            TCP_Socket3, addr = serverSocket.accept()
            received = TCP_Socket3.recv(2048)
            received = received.decode()

def tcp_conn():
    # establish connection
    TCP_Socket2 = socket(AF_INET, SOCK_STREAM)
    TCP_Socket2.connect((serverName, serverPort))
    received = TCP_Socket2.recv(2048)
    received = received.decode()
    currPort = int(received)
    TCP_Socket2.close()
    return currPort
            

            
if __name__ == "__main__":
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    auth = False
    currPort = tcp_conn()
    time.sleep(1)
    TCP_Socket = socket(AF_INET, SOCK_STREAM)
    TCP_Socket.connect((serverName, currPort))
    t1 = threading.Thread(target=receiveFunction)
    t1.setDaemon(True)
    t1.start()
    while True:
        time.sleep(1)
        if (not auth):
            # get auth information
            authInfo = []
            authInfo.append(input("Username: "))
            authInfo.append(input("Password: "))
            TCP_Socket.send(pickle.dumps(authInfo))
        else:
            try:
                mes = input()
                TCP_Socket.send(mes.encode())
                if mes == "logout":
                    throw()
                    TCP_Socket.close()
            except OSError:
                sys.exit()