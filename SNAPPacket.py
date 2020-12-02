mask4bits = ((1 << 4) -1)
import numpy as np

mask8bits = ((1 << 8) -1)
mask16bits = ((1 << 16) -1)
mask64bits = ((1 << 64) -1)

class SNAPPacket(object):
    """
    ATA SNAP Firmware Manual, Release 2.0.0
    ---------------------------------------
    Section 2.3.2 "Output Data Formats: Voltage Packets", pg 5
    https://github.com/realtimeradio/ata_snap/blob/nov-observing/docs/manual.pdf

    struct voltage_packet {
        uint8_t version;
        uint8_t type;
        uint16_t n_chans;
        uint16_t chan;
        uint16_t feng_id
        uint64_t timestamp;
        complex4 data[n_chans, 16, 2] // 4-bit real + 4-bit imaginary
    };

    • version; Firmware version: Bit [7] is always 1 for Voltage packets. The remaining bits contain a
    compile-time defined firmware version, represented in the form bit[6].bits[5:3].bits[2:0]. This document
    refers to firmware version 2.0.0.
    • type; Packet type: Bit [0] is 1 if the axes of data payload are in order [slowest to fastest] channel x time x
    polarization. This is currently the only supported mode. Bit [1] is 0 if the data payload comprises 4+4 bit
    complex integers. This is currently the only supported mode.
    • n_chans; Number of Channels: Indicates the number of frequency channels present in the payload of
    this data packet.
    • chan; Channel number: The index of the first channel present in this packet. For example, a channel
    number c implies the packet contains channels c to c + n_chans - 1.
    • feng_id; Antenna ID: A runtime configurable ID which uniquely associates a packet with a particular
    SNAP board.
    • timestamp; Sample number: The index of the first time sample present in this packet. For example, a
    sample number 𝑠 implies the packet contains samples 𝑠 to 𝑠 + 15. Sample number can be referred to GPS
    time through knowledge of the system sampling
    """

    def __init__(self,
                 fwVersion: int = None,
                 packetType: bool = None,
                 channels: int = None,
                 channelNum: int = None,
                 fEngineId: int = None,
                 packetNumber: int = None,
                 samples: [int] = None,
                 packetBytes: bytearray = None,
                 byteorder: str = 'big'
                 ):
        self.bytearr = bytearray(8192+16)
        self.payloadbytes = -1
        if packetBytes is not None:
            self.setHeader(
                int.from_bytes(packetBytes[0:1], byteorder=byteorder),
                int.from_bytes(packetBytes[1:2], byteorder=byteorder),
                int.from_bytes(packetBytes[2:4], byteorder=byteorder),
                int.from_bytes(packetBytes[4:6], byteorder=byteorder),
                int.from_bytes(packetBytes[6:8], byteorder=byteorder),
                int.from_bytes(packetBytes[8:16], byteorder=byteorder)
                )
            self.setSampleBytes(packetBytes[16:])

        else:
            if not self.setHeader(fwVersion, packetType, channels, channelNum, fEngineId, packetNumber):
                exit()
            if not self.setSamples(samples):
                exit()

    def setHeader(self,
                  fwVersion: int = None,
                  packetType: bool = None,
                  channels: int = None,
                  channelNum: int = None,
                  fEngineId: int = None,
                  packetNumber: int = None,
                  update: bool = False
                  ):
        
        notAllArgs = False

        if fwVersion is not None:
            self.fwVersion = fwVersion & mask8bits
            self.bytearr[0] = self.fwVersion
        else:
            notAllArgs = True

        if packetType is not None:
            self.packetType = (3 if packetType else 0) & mask8bits
            self.bytearr[1] = self.packetType
        else:
            notAllArgs = True

        if channels is not None:
            self.channels = channels & mask16bits
            self.bytearr[2] = (self.channels >> 8) & mask8bits
            self.bytearr[3] = self.channels & mask8bits
        else:
            notAllArgs = True

        if channelNum is not None:
            self.channelNum = channelNum & mask16bits
            self.bytearr[4] = (self.channelNum >> 8) & mask8bits
            self.bytearr[5] = self.channelNum & mask8bits
        else:
            notAllArgs = True

        if fEngineId is not None:
            self.fEngineId = fEngineId & mask16bits
            self.bytearr[6] = (self.fEngineId >> 8) & mask8bits
            self.bytearr[7] = self.fEngineId & mask8bits
        else:
            notAllArgs = True

        if packetNumber is not None:
            self.packetNumber = packetNumber & mask64bits
            self.bytearr[ 8] = (self.packetNumber >> 56) & mask8bits
            self.bytearr[ 9] = (self.packetNumber >> 48) & mask8bits
            self.bytearr[10] = (self.packetNumber >> 40) & mask8bits
            self.bytearr[11] = (self.packetNumber >> 32) & mask8bits
            self.bytearr[12] = (self.packetNumber >> 24) & mask8bits
            self.bytearr[13] = (self.packetNumber >> 16) & mask8bits
            self.bytearr[14] = (self.packetNumber >> 8) & mask8bits
            self.bytearr[15] = self.packetNumber & mask8bits
        else:
            notAllArgs = True
        
        self.payloadbytes = self.channels * 2 * 16

        if notAllArgs and not update:
            print("Please provide all of the header's arguments.");
            self.payloadbytes = -1
            return False

        return True

    def setSamples(self, samples):
        if len(samples)/2 != self.payloadbytes:
            print("Header inferred payload byte size {} differs from samples length {}\n".format(
                self.payloadbytes, len(samples)/2
            ))
            return False
        for sampleI in range(self.payloadbytes):
            self.bytearr[16+sampleI] = ((samples[2*sampleI] & mask4bits) << 4) + (samples[2*sampleI+1] & mask4bits)
        return True

    def setSampleBytes(self, samples):
        if len(samples) != self.payloadbytes:
            print("Header inferred payload byte size {} differs from samples length {}\n".format(
                self.payloadbytes, len(samples)
            ))
            return False
        self.bytearr[16:self.payloadbytes] = samples
        return True

    def packet(self):
        return self.bytearr[:16+self.payloadbytes]
    
    def print(self, headerOnly=False):
        if headerOnly:
            print(self.headerStr())
        else:
            print(self.str())

    def twosCompliment(self, value, bits):
        return value if value < (1<<(bits-1)) else (value % (1<<(bits-1))) - (1<<(bits-1))

    def str(self):
        return """{}
            \rSamples (0x): {}""".format(self.headerStr(),
                                        [complex(self.twosCompliment(i>>4, 4) , self.twosCompliment(i & mask4bits, 4)) 
                                        for i in self.bytearr[16:self.payloadbytes]])

    def headerStr(self):
        return """Firmware Version: {}
            \rPacket type: {}
            \rNumber of Channels: {}
            \rChannel number: {}
            \rAntenna ID: {}
            \rPacket number: {}
            \rPayload bytes: {}""".format(self.fwVersion,
                                        self.packetType,
                                        self.channels,
                                        self.channelNum,
                                        self.fEngineId,
                                        self.packetNumber,
                                        self.payloadbytes)
    def update(self,
               fwVersion: int = None,
               packetType: bool = None,
               channels: int = None,
               channelNum: int = None,
               fEngineId: int = None,
               packetNumber: int = None,
               samples: [int] = None
               ):
        self.setHeader(fwVersion, packetType, channels, channelNum, fEngineId, packetNumber, update=True)
        if samples is not None:
            self.setSamples(samples)

if __name__ == '__main__':
    testPacket = SNAPPacket(
        0,
        True,
        2,
        2,
        0,
        3735928559,
        [i % 16 for i in range(16*2*2)]
    )
    testPacket.print()
    testPacketBytes = testPacket.packet()
    dupPacket = SNAPPacket(packetBytes=testPacketBytes)
    dupPacket.print()
    dupPacketBytes = dupPacket.packet()
    print(testPacketBytes)
    print(dupPacketBytes)
