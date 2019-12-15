#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from socket import *
import time
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
rtt_1 =[]

for i in range(10):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(1)
    sendtime = time.time()
    message = "PING" +str(i)+ ' '+time.asctime() +'\r\n'
    clientSocket.sendto(message.encode(),(serverName, serverPort))
    try:
        received, serverAddress = clientSocket.recvfrom(2048)
        rtt = (time.time() - sendtime) * 1000 
        rtt_1.append(rtt)
        print(f'ping to {serverName}, seq = {i}, rtt = {rtt:.0f} ms')
    except timeout:

        print(f'ping to {serverName}, seq = {i}, time out')
    

print(f'Minimum RTT = {min(rtt_1)} ms')
print(f'Maximum RTT = {max(rtt_1)} ms')
print(f'Average RTT = {round(float(sum(rtt_1) / len(rtt_1)))} ms')
clientSocket.close()
