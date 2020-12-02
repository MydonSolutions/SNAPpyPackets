#https://wiki.python.org/moin/UdpCommunication

import socket
from SNAPPacket import SNAPPacket

UDP_IP = "0.0.0.0"
UDP_PORT = 4015

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(8192+16) # buffer size is 8192 bytes
    # print("received message: %s" % data)
    SNAPPacket(packetBytes = data).print(True)
    # if "n" in input("Continue (Y/n)? "):
    #   break
