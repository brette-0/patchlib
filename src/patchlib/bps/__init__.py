"""
experimental alpha bps handler
"""

__version__ = "0.1"

def encode(data : int) -> bytearray:  #create function return bytearray, takes int

    encoded = b""                       #create bytearray for return
    while True:                         #create indefinte loop
        x = data & 0x7f                 #create temporary variable "x" with "content" of byte | taking it's lower 7LSBs
        data >>= 7                      #trim last 7 bytes off
        if data == 0:                   #if data is equivalent to zero, write signed MSB + stored 7 LSBs
            encoded+=bytes([0x80 | x])  
            break                       #exit loop
        encoded+=bytes([x])             #else if not end, loop after appending stored 7lSBs with
        data-=1                         #decrement at the end
    return encoded                      #return bytearray of encoded contents


def decode(Bytes: bytes) -> int:
    data, shift = 0, 1
    index = 0
    while True:
        x = Bytes[index]
        data += (x & 0x7f) * shift
        index += 1
        if x & 0x80:
            break
        shift <<= 7
        data += shift
    return data


class bps:
    class SourceRead: 
        def __init__(self, parent, length): self.parent,self.length = parent, length
    class TargetRead: 
        def __init__(self, parent, length): self.parent,self.length = parent, length
    class SourceCopy: pass
    class TargetCopy: pass

    def __init__(self, source : bytes):

        trim = lambda: source[source.index([byte for byte in source[:16] if byte & 128][0])+1:]   #trim bps from first d0 enabled byte
        
        normalized = {};bps = bps[4:]
        normalized["Source Size"] = decode(bps[:16]);source = trim()    #Decode Source Size   | read 16 bytes ahead for u128i
        normalized ["Target Size"] = decode(bps[:16]);source = trim()   #Decode Target Size   | read 16 bytes ahead for u128i
        normalized ["Metadata Size"] = decode(bps[:16]);source = trim() #Decode Metadata Size | read 16 bytes ahead for u128i
        
    
        normalized["Metadata"] = bps[:normalized["Metadata Size"]]              #Gather Metadata as bytearray (should be xml | may not be)
        source = source[normalized["Metadata Size"]:]                                 #trim bps to exclude metadata

        normalized["source-checksum"] = source[-24:-16]                            #Source file checksum
        normalized["target-checksum"] = source[-16:-8]                             #Target file checksum 
        normalized["patch-checksum"] = source[-8:]                                 #bps file checksum

        source = source[:-24]                                                         #trim Footer
        




#Some chatGPT churned out code, yet to modify
def sourceCopy(length: int) -> bytes:
    global source, sourceOffset
    if sourceOffset + length > len(source):
        raise ValueError("Invalid source offset")
    data = source[sourceOffset:sourceOffset+length]
    sourceOffset += length
    return data

def targetCopy(length: int) -> bytearray:
    global target, targetOffset
    data = bytearray(target[targetOffset:targetOffset+length])
    targetOffset += length
    return data

def sourceCopy(relativeOffset: int, length: int) -> None:
    global source_offset, target_offset

    source_offset += relativeOffset
    if source_offset < 0 or source_offset + length > len(source):
        raise ValueError("Invalid source offset")

    target[target_offset:target_offset+length] = source[source_offset:source_offset+length]
    target_offset += length


def targetCopy(relativeOffset: int, length: int) -> None:
    global target_offset

    target_offset += relativeOffset
    if target_offset < 0 or target_offset + length > len(target):
        raise ValueError("Invalid target offset")

    target[target_offset:target_offset+length] = target[target_offset-target_offset:target_offset+length-target_offset]
    target_offset += length