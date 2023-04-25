"""
in-dev bps beta
"""

__version__ = "0.5"


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
    def __iter__(self): return iter(self.operations)
    class source_read: 
        def __init__(self, parent, length, outputOffset, name): 
            self.parent, self.length, self.outputOffset, self.name = parent, length, outputOffset, name
    class target_read: 
        def __init__(self, parent, length, outputOffset, data, name): 
            self.parent, self.length, self.outputOffset, self.data, self.name  = parent, length, outputOffset, data, name
    class source_copy: 
        def __init__(self, parent, length, outputOffset, relativeOffset, name):
           self.parent, self.length, self.outputOffset, self.relativeOffset, self.name = parent, length, outputOffset, relativeOffset, name
    class target_copy(source_copy): 
        def __init__(self, parent, length, outputOffset, relativeOffset, name):
            super().__init__(parent, length, outputOffset, relativeOffset, name)

    def __init__(self, patch : bytes, checks : bool = True):

        self.operations = [];outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None].hex() for i in range(-12, 0, 4)];patch = patch[4:-12]
        trim = lambda: patch[patch.index([byte for byte in patch[:16] if byte & 128][0])+1:]   #trim bps from first d0 enabled byte

        self.sourceSize = decode(patch[:16]); patch = trim()                    # Decode Source Size   | read 16 bytes ahead for u128i
        self.targetSize = decode(patch[:16]); patch = trim()                    # Decode Target Size   | read 16 bytes ahead for u128i
        self.metadataSize = decode(patch[:16]); patch = trim()                  # Decode Metadata Size | read 16 bytes ahead for u128i


        if self.metadataSize:
            self.metadata = patch[:self.metadataSize];patch = patch[self.metadataSize:]     # Gather Metadata as bytearray (should be xml | may not be)


        while self.targetSize-outputOffset:                                                 # While there is still data subject to normalisation
            operation = decode(patch[:16]);patch = trim()                                   # Decode operation  | read 16 bytes ahead for u128i
            length = (operation >> 2) + 1                                                   # Determine length
            args = [self, length, outputOffset]                                             # Assume default args
            if operation & 2:                                                               # If a copy function
                relativeOffset = decode(patch[:16]);patch = trim()                          # Decode the modifier
                relativeOffset = (relativeOffset >> 1) * (-1 if relativeOffset & 1 else 1)  # Process modifier
                if operation & 1: targetRelativeOffset += relativeOffset                    # Modify Appropriate relativeOffset
                else: sourceRelativeOffset += relativeOffset
                args.append(targetRelativeOffset if operation & 1 else sourceRelativeOffset)# Add value to normalized data
            elif operation & 1:                                                             # If target_read
                args.append(patch[:length]);patch = patch[length:]                          # Append the actual data and trim patch accordingly
            outputOffset += length                                                          # Increase variable counter to indicate 
            self.operations.append(eval(("self.source_read","self.target_read","self.source_copy","self.target_copy")[operation & 3])(*args,
                                name=f"Unnamed {('self.source_read','self.target_read','self.source_copy','self.target_copy')[operation&3]} at {outputOffset}"))

            
        self.operations = tuple(self.operations)                                  #Memory efficiency

        

def apply(patch : bps, source : bytes, checks : bool = True) -> tuple:
    target = b"";outputOffset = sourceRelativeOffset = targetRelativeOffset = 0

    if len(source) != patch.sourceSize and checks: raise ValueError()
    if crc32(source) != patch.source_checksum and checks: raise ValueError()
    #patch corruption mechanic lost - but is that a bad thing entirely?


    def source_read(operation : bps.source_read): 
        nonlocal source, target
        target += source[operation.outputOffset:operation.outputOffset + operation.length]
    def target_read(operation : bps.target_read): 
        nonlocal target
        target += operation.data
    def source_copy(operation : bps.source_copy): 
        nonlocal source, target, sourceRelativeOffset
        sourceRelativeOffset += operation.relativeOffset
        target += source[sourceRelativeOffset:sourceRelativeOffset+operation.length]
    def target_copy(operation : bps.target_copy):
        nonlocal target, targetRelativeOffset
        nonlocal targetRelativeOffset
        targetRelativeOffset += operation.relativeOffset
        target += source[targetRelativeOffset:targetRelativeOffset+operation.length]


    for operation in patch:
        (source_read,target_read,source_copy,target_copy)[(bps.source_read,bps.target_read,bps.source_copy,bps.target_copy).index(operation.__class__)](operation)

    return (target, patch.metadata) if hasattr(patch, "metadata") else (target,)


def apply_old(patch: bytes, source: bytes, checks : bool = True) -> bytes: 
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
