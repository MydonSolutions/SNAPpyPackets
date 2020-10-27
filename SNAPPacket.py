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
                 sampleNumber: int = None,
                 samples: [int] = None,
                 bytes: bytearray = None,
                 byteorder: str = 'big'
                 ):
        
        if bytes is not None:
            self.fwVersion = int.from_bytes((bytes[0:1]), byteorder=byteorder)
            self.packetType = int.from_bytes((bytes[1:2]), byteorder=byteorder)
            self.channels = int.from_bytes((bytes[2:4]), byteorder=byteorder)
            self.channelNum = int.from_bytes((bytes[4:6]), byteorder=byteorder)
            self.fEngineId = int.from_bytes((bytes[6:8]), byteorder=byteorder)
            self.sampleNumber = int.from_bytes((bytes[8:24]), byteorder=byteorder)
            self.samplesHex = bytes[24:].hex()

            self.headerHex = [
                bytes[0:1].hex(),
                bytes[1:2].hex(),
                bytes[2:4].hex(),
                bytes[4:6].hex(),
                bytes[6:8].hex(),
                bytes[8:24].hex()
            ]
        else:
            self.fwVersion = fwVersion & mask8bits
            self.packetType = (1 if packetType else 0) & mask8bits
            self.channels = channels & mask16bits
            self.channelNum = channelNum & mask16bits
            self.fEngineId = fEngineId & mask16bits
            self.sampleNumber = sampleNumber & mask64bits
            self.samplesHex = [format(sample & mask4bits, 'x')
                            for sample in samples]

            self.headerHex = [
                format(self.fwVersion, 'x').zfill(2),
                format(self.packetType, 'x').zfill(2),
                format(self.channels, 'x').zfill(4),
                format(self.channelNum, 'x').zfill(4),
                format(self.fEngineId, 'x').zfill(4),
                format(self.sampleNumber, 'x').zfill(16)
            ]

    def toBytes(self):
        return bytes.fromhex(''.join(self.headerHex + self.samplesHex))
    
    def print(self):
        print(self.str())

    def str(self):
        return """Firmware Version: {}
            \rPacket type: {}
            \rNumber of Channels: {}
            \rChannel number: {}
            \rAntenna ID: {}
            \rSample number: {}
            \rSamples (0x): {}\n""".format(self.fwVersion,
                                        self.packetType,
                                        self.channels,
                                        self.channelNum,
                                        self.fEngineId,
                                        self.sampleNumber,
                                        self.samplesHex)

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
    testPacketBytes = testPacket.toBytes()
    print(testPacketBytes)
    SNAPPacket(bytes=testPacketBytes).print()