#https://wiki.python.org/moin/UdpCommunication

import socket
from SNAPPacket import SNAPPacket

UDP_IP = "127.0.0.1"
UDP_PORT = 6666

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(8192) # buffer size is 8192 bytes
    print("received message: %s" % data)
    SNAPPacket(packetBytes = data).print()
    if "n" in input("Continue (Y/n)? "):
      break
