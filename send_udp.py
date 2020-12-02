import socket
from SNAPPacket import SNAPPacket
import time

channels = 256

def alternate(i, evenVal, oddVal):
    return evenVal if i%2==0 else oddVal

def int8Comp4(i, realMul, realDiv, realBias, imagMul, imagDiv, imagBias):
    return alternate(i, (int((realMul*i)/realDiv) + realBias)%8, (int((imagMul*i)/imagDiv) + imagBias)%8)


def createPacket(fengId, nchan, schan, real, sampleNumber=0):
    return SNAPPacket(
        0,              #fwVersion
        True,           #packetType is voltage
        nchan,          #channels
        schan,          #channelNum
        fengId,         #fEngineId
        sampleNumber,   #sampleNumber        
        [alternate(i, real, chanI + 8*(chanI%2))#conjugate every second channel
            for chanI in range(nchan) for i in range(16*2*2)]
    )

cachedSampleIs = 1

packets = [createPacket(fengI, channels, channels*strmI, sampleI, sampleI*16) 
            for sampleI in range(cachedSampleIs) for strmI in range(1) for fengI in range(1)]

UDP_IP = "10.11.1.156"
UDP_PORT = 4015
MESSAGE = packets[0].packet()

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print(len(packets), "different packets.")

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


start = time.time()

while('y' in input("Send Block? ")):
    for pktI in range(0, 16384):
        for packet in packets:
            sock.sendto(packet.packet(), (UDP_IP, UDP_PORT))
            # sock.sendto(b'hello', (UDP_IP, UDP_PORT))
            packet.update(packetNumber=packet.packetNumber+(16*cachedSampleIs))
            time.sleep(0.00001)

print(time.time() - start)