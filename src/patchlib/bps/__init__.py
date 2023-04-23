"""
in-dev bps beta
"""

__version__ = "0.3"


from zlib import crc32

def encode(number : int) -> bytes:
    """
	Convert number into variable-width encoded bytes
    """

    if not isinstance(number,int): raise TypeError("Number data must be integer")
    if number < 0: raise ValueError("Cannot convert negative number!")
	
    var_length = b""							#Create empty bytes object to store variable-width encoded bytes
    while True:									#Until we are finished
        x = number & 0x7f						#Using the 7 LSB of the number
        number >>= 7							#And removing such data
        if number: 								#If there is still source data to read
            var_length += x.to_bytes(1, "big")	#Append such data to our bytes object
            number -= 1							#Decrement by one to remove ambiguity
        else: 
            var_length += (0x80 | x).to_bytes(1, "big")	#Set termination byte
            break 										#Final data is wronte, leave
    return var_length									#return our variable-width encoded data


def decode(encoded : bytes) -> int:
    """
	Decode variable-width encoded bytes into unsinged integer
    """
    if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")

    number = 0								    #Assume 0 for operational efficiency 
    shift = 1
    for byte in encoded:					    #for each byte in our given data
        number += (byte & 0x7f) * shift		    #increase number by data bits
        if byte & 0x80: break				    #break if termination bytes set
        shift <<= 7
        number += shift
    return number							    #return decoded number

class bps:
    class source_read: 
        def __init__(self, parent, length, outputOffset): self.parent, self.length, self.outputOffset = parent, length, outputOffset
    class target_read: 
        def __init__(self, parent, length, outputOffset): self.parent, self.length, self.outputOffset = parent, length, outputOffset
    class source_copy: 
        def __init__(self, parent, length, outputOffset, relativeOffset): self.parent, self.length, self.outputOffset, self.relativeOffset = parent, length, outputOffset, relativeOffset
    class target_copy: 
        def __init__(self, parent, length, outputOffset, relativeOffset): self.parent, self.length, self.outputOffset, self.relativeOffset = parent, length, outputOffset, relativeOffset

    def __init__(self, patch : bytes):

        self.actions = [];outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None] for i in range(-12, 0, 4)];patch = patch[4:-12]
        trim = lambda: patch[patch.index([byte for byte in patch[:16] if byte & 128][0])+1:]   #trim bps from first d0 enabled byte

        self.sourceSize = decode(patch[:16]); patch = trim()                    # Decode Source Size   | read 16 bytes ahead for u128i
        self.targetSize = decode(patch[:16]); patch = trim()                    # Decode Target Size   | read 16 bytes ahead for u128i
        self.metadataSize = decode(patch[:16]); patch = trim()                  # Decode Metadata Size | read 16 bytes ahead for u128i

        if self.metadataSize:
            self.metadata = patch[:self.metadataSize];patch = patch[self.metadataSize:]   # Gather Metadata as bytearray (should be xml | may not be)

        while len(patch):
            operation = decode(patch[:16]);patch = trim() 
            length = (operation >> 2) + 1  
            args = [self, length, outputOffset]
            if operation & 2: 
                if operation & 1: 
                     args.append(targetRelativeOffset)
                     targetRelativeOffset += length
                else:
                    args.append(sourceRelativeOffset)
                    sourceRelativeOffset += length
            self.actions.append((self.source_read,self.target_read,self.source_copy,self.target_copy)[operation & 3](*args)) 
            outputOffset += length;patch = patch[length:]
        self.actions = tuple(self.actions)                                  #Memory efficiency

        





def apply(patch: bytes, source: bytes, checks : bool = True) -> bytes: 
    """
    Applies BPS Patch to source file
    """

    target = bytearray(source);outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
    source_checksum, target_checksum, patch_checksum = [patch[i:i+4 if i+4 else None] for i in range(-12, 0, 4)];patch = patch[4:-12]
    if not all(crc32(component) == int(goal.hex(),16) for component,goal in ((patch,patch_checksum),(source,source_checksum))) and checks: raise ValueError("Sourcefile or Patchfile corrupt")
    trim = lambda: patch[patch.index([byte for byte in patch[:16] if byte & 128][0])+1:]   #trim bps from first d0 enabled byte

    sourceSize = decode(patch[:16]); patch = trim()                    # Decode Source Size   | read 16 bytes ahead for u128i
    targetSize = decode(patch[:16]); patch = trim()                    # Decode Target Size   | read 16 bytes ahead for u128i
    metadataSize = decode(patch[:16]); patch = trim()                  # Decode Metadata Size | read 16 bytes ahead for u128i

    if len(source) != sourceSize and checks: raise ValueError("Sourcefile is of unacceptable filesize")

    if metadataSize:
        metadata = patch[:metadataSize];patch = patch[metadataSize:]  # Gather Metadata as bytearray (should be xml | may not be)
    else: metadata = None


    def source_read() -> None:
        nonlocal length,source,target,outputOffset
        target[outputOffset:outputOffset+length] = source[outputOffset:outputOffset+length]
        outputOffset += length


    def target_read():
        nonlocal length, outputOffset, target, patch
        target[outputOffset:outputOffset+length] = patch[:length];patch = patch[length:]
        outputOffset += length
        

    def source_copy() -> None:
        nonlocal length, outputOffset, sourceRelativeOffset, patch, trim
        data = decode(patch[:16]);patch = trim() 
        sourceRelativeOffset = (data >> 1) * (-1 if data & 1 else 1)
        target[outputOffset:outputOffset+length] = source[sourceRelativeOffset:sourceRelativeOffset+length] 
        outputOffset += length;sourceRelativeOffset += length


    def target_copy() -> None:
        nonlocal length, outputOffset, targetRelativeOffset, patch, trim
        data = decode(patch[:16]);patch = trim() 
        targetRelativeOffset = (data >> 1) * (-1 if data & 1 else 1)
        target[outputOffset:outputOffset+length] = source[targetRelativeOffset:targetRelativeOffset+length] 
        outputOffset += length;targetRelativeOffset += length

    while len(patch):
        operation = decode(patch[:16]);patch = trim() 
        length = (operation >> 2) + 1  
        (source_read,target_read,source_copy,target_copy)[operation & 3]()
        

    return target, source_checksum, target_checksum, patch_checksum, metadata