import socket
from SNAPPacket import SNAPPacket
import time

channels = 256

packet1 = SNAPPacket(
    0,          #fwVersion
    True,       #packetType is voltage
    channels,   #channels
    0,          #channelNum
    0,          #fEngineId
    0,          #sampleNumber        
    [int(i/16) % 16 for i in range(16*2*2*channels)]
)

UDP_IP = "127.0.0.1"
UDP_PORT = 4015

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
# print("message: %s" % MESSAGE)
packet1.print()

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

packet1.print()
while True:
    sock.sendto(packet1.packet(), (UDP_IP, UDP_PORT))
    packet1.update(packetNumber=packet1.packetNumber+16)
    time.sleep(0.0001)
