from socket import *
import pickle
import sys
import threading
import collections
import time

#####check if the mame in block list
def check_in_list(user,receive):
    name_list = []
    for i in user.keys():
        name_list.append(i)
    if receive not in name_list:
        return 0
    else:
        return 1

######logout broadcast
def broadcast_logout(user,user_name):
    for i in user.keys():
        if user[i]["status"] == "online":
            return_message = f"{user_name} logged out\n"
            #print(user[i]["port"])
            user[i]["socket"].send(return_message.encode())

######timeout proceess
def handle_timeout(user,timeout_time):
    while 1:
        time.sleep(1)
        for i in user.keys():
            if user[i]['status']=="online":
                #print(user[i]['status'])
                if user[i]['active_time'] > 0:
                    if time.time() - user[i]['active_time'] > timeout_time:
                        user[i]['status'] = "offline"
                        user[i]["logout"] = time.time()
                        return_message = f'Your connection is timeout,please tap Enter button'
                        try:
                            user[i]["socket"].send(return_message.encode())
                            user[i]["socket"].close()
                        except OSError:
                            pass

######send the online status to other user
def broadcast_login(user,user_name):
    for i in user.keys():
        if user[i]["status"] == "online" and i != user_name:
            return_message = f"{user_name} logged in\n"
            #print(user[i]["port"])
            user[i]["socket"].send(return_message.encode())
        
#####the configuration of user
def auth(conn_soc,user_name,user_password,user):
   
    if user_name not in user.keys():
        return 0,"Error. Invalid user"

    if user_password!= user[user_name]['password']:
        user[user_name]["log_in_time"] += 1
        #print(user[user_name]["log_in_time"])
        if user[user_name]["log_in_time"] >= 3:
            user[user_name]['status'] = "block"
            user[user_name]['ban'] = time.time()
            return 0,"Invalid Password. Your account has been blocked. Please try again later\n"
        return 0,"Invalid Password. Please try again\n"
        
    if user[user_name]["password"] == user_password:
        if user[user_name]['status'] != "online":
            if type(user[user_name]['ban']) ==float:
                if time.time() - user[user_name]['ban'] >= block_duration:
                    user[user_name]["port"] = currPort
                    user[user_name]['status'] = "online"
                    user[user_name]['active_time'] = time.time()
                    user[user_name]["log_in_time"] = 0
                    user[user_name]["socket"] = conn_soc
                    return 1,"Welcome to the greatest messaging application ever!\n"
                else:
                    return 0,"Your account is blocked due to multiple login failures. Please try again later\n"
            else:
                user[user_name]["port"] = currPort
                user[user_name]['status'] = "online"
                user[user_name]['active_time'] = time.time()
                user[user_name]["log_in_time"] = 0
                user[user_name]["socket"] = conn_soc
                return 1,"Welcome to the greatest messaging application ever!\n"
        else:
            return 0, "user already logged in\n"


####process the command
def tcp(serverSocket,conn_soc,user,timeout):
    while True:
        try:
            user_info= pickle.loads(conn_soc.recv(1024))
        except Exception:
            break
        user_name = user_info[0]
        user_password = user_info[1]
        
        #print(user_info)
        status, message = auth(conn_soc,user_name,user_password,user)
        
        if status == 1:####success login
            #login time
            user[user_name]["login"] = time.time()
            block_list = []
            
            #print(user)
            broadcast_login(user,user_name)
            return_message = message.encode()
            conn_soc.send(return_message)
            #handle the offline message
            if user[user_name]["status"] == "online":
                for i in user[user_name]["offline_msg"]:
                    user[user_name]["socket"].send(i.encode())

            while True:
                try:
                    received = conn_soc.recv(2048)
                except OSError:
                    print("connection has closed")
                    break
                received = received.decode()
                received = received.split()
                #print(received)
                try:
                    try:
                        if "message" == received[0] and user_name not in user[received[1]]["block"]:
                            try:
                                return_message = f'{user_name}: {" ".join(received[2:])}'
                                user[user_name]["active_time"] = time.time()
                                user[received[1]]["socket"].send(return_message.encode())
                                
                            except Exception:
                                return_message = f'{user_name}: {" ".join(received[2:])}\n'
                                user[user_name]["active_time"] = time.time()
                                user[received[1]]["offline_msg"].append(return_message)

                        elif "block" == received[0] and received[1] != user_name and check_in_list(user,received[1]):
                            block_list.append(received[1])
                            user[user_name]["active_time"] = time.time()
                            user[user_name]["block"].append(received[1])
                            return_message = f'{received[1]} is blocked'
                            user[user_name]["socket"].send(return_message.encode())

                        elif "message" == received[0] and user_name in user[received[1]]["block"]:
                            user[user_name]["active_time"] = time.time()
                            return_message = f'Your  message  could  not be delivered as the recipient has blocked you'
                            user[user_name]["socket"].send(return_message.encode())
                            
                        elif "block" == received[0] and received[1] == user_name and check_in_list(user,received[1]):
                            user[user_name]["active_time"] = time.time()
                            return_message = f'Error. Cannot block self'
                            user[user_name]["socket"].send(return_message.encode())

                        elif "unblock" == received[0] and received[1] not in user[user_name]["block"]:
                            user[user_name]["active_time"] = time.time()
                            return_message = f'Error. {received[1]} was not blocked '
                            user[user_name]["socket"].send(return_message.encode())

                        elif "unblock" == received[0] and received[1]in user[user_name]["block"]:
                            user[user_name]["active_time"] = time.time()
                            return_message = f'{received[1]} is unblocked '
                            user[user_name]["socket"].send(return_message.encode())
                            user[user_name]["block"].remove(received[1])

                        elif "broadcast" == received[0] and received[1] in block_list:
                            user[user_name]["active_time"] = time.time()
                            return_message = f'Your message  could  not be  delivered  to  some recipients'
                            user[user_name]["socket"].send(return_message.encode())
                            #print(1)
                            for i in user.keys():
                                if user[i]["status"] == "online" and i != user_name and user_name not in user[i]["block"]:
                                    return_message = f'{user_name}: {" ".join(received[1:])}'
                                    user[i]["socket"].send(return_message.encode())

                        elif "broadcast" == received[0] and received[1] not in block_list:
                            user[user_name]["active_time"] = time.time()
                            #print(block_list)
                            for i in user.keys():
                                if user[i]["status"] == "online" and i != user_name:
                                    #print(2)
                                    return_message = f'{user_name}: {" ".join(received[1:])}'
                                    user[i]["socket"].send(return_message.encode())

                        elif "whoelse" == received[0]:
                            user[user_name]["active_time"] = time.time()
                            for i in user.keys():
                                if user[i]["status"] == "online" and i != user_name:
                                    return_message = f'{i}'
                                    user[user_name]["socket"].send(return_message.encode())
                        
                        elif "logout" == received[0]:
                            user[user_name]["active_time"] = time.time()
                            user[user_name]["status"] = "offline"
                            user[user_name]["logout"] = time.time()
                            broadcast_logout(user,user_name)
                            conn_soc.close()
                        
                        elif "whoelsesince" == received[0]:
                            for i in user.keys():
                                if time.time() - float(received[1]) < user[i]["login"] and i != user_name:
                                    return_message = f'{i}\n'
                                    user[user_name]["socket"].send(return_message.encode())

                        elif "startprivate" == received[0] and user[received[1]]["status"] == "online" and received[1] not in block_list:
                            pass
                            

                        elif "private" == received[0]:
                            return_message = f'Error. Private messaging to {received[1]} not enabled'
                            user[user_name]["socket"].send(return_message.encode())

                        else:
                            user[user_name]["active_time"] = time.time()
                            return_message = f'Error. Invalid command'
                            user[user_name]["socket"].send(return_message.encode())

                    except KeyError:
                        user[user_name]["active_time"] = time.time()
                        return_message = f'Error. Invalid user'
                        user[user_name]["socket"].send(return_message.encode())
                except IndexError:
                    user[user_name]["socket"].close()
            #conn_soc.settimeout(timeout)######time out
        else:#####failure login
            conn_soc.send(message.encode())
            
        
        

            
def each_client(currPort,user,timeout):
    #welcome socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((serverName, currPort))
    serverSocket.listen(0) 
    #print(currPort)
    

    ####add time out function
    while True:
        connectionSocket, addr = serverSocket.accept()#current connection
        t = threading.Thread(target = tcp,args = (serverSocket,connectionSocket,user,timeout))
        t.setDaemon(True)
        t.start()

def main(server_port,block_duration,time_out):
    global currPort
    user = dict()
    serverName = "localhost"
    with open('credentials.txt') as file:
        for i in file:
            i = i.rstrip()
            i = i.split(' ')
            user[i[0]] = {}
            user[i[0]]["password"] = i[1]
            user[i[0]]["status"] = "offline"#online 1; offline2;blocked3
            user[i[0]]["ban"] = ''
            user[i[0]]["active_time"] = ''
            user[i[0]]["log_in_time"] = 0
            user[i[0]]["port"] = 0
            user[i[0]]["socket"] = None
            user[i[0]]["block"] = []
            user[i[0]]["offline_msg"] = [] 
            user[i[0]]["login"] = 0 
            user[i[0]]["logout"] = 0 
            
    #print(user)
    
    ##setuo welcome socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((serverName, server_port))
    serverSocket.listen(0)
    timeout = threading.Thread(target=handle_timeout, args=(user,time_out))
    timeout.setDaemon(True)
    timeout.start()

    #give each client a new port num
    while True:
        connectionSocket, addr = serverSocket.accept()
        connectionSocket.send(str(currPort).encode())
        connectionSocket.close()
        t1 = threading.Thread(target = each_client, args=(currPort,user,time_out))
        t1.setDaemon(True)
        t1.start()
        currPort += 1
            

            
if __name__ == "__main__":
    serverName = "localhost"
    server_port = int(sys.argv[1])
    currPort = int(sys.argv[1]) + 1
    block_duration = int(sys.argv[2])
    time_out =  int(sys.argv[3])
    private_port = 7000
    

    #three parameters
    main(server_port,block_duration,time_out)
    
    
  