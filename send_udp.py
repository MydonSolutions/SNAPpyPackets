import socket
from SNAPPacket import SNAPPacket

testPacket = SNAPPacket(
    0,
    True,
    2,
    2,
    0,
    3735928559,
    [i % 16 for i in range(16*2*2)]
)

UDP_IP = "127.0.0.1"
UDP_PORT = 6666
MESSAGE = testPacket.packet()

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))