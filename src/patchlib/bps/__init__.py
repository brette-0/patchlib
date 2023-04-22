"""
experimental alpha bps handler
"""

__version__ = "0.3"

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
    class SourceRead: 
        def __init__(self, parent, length): self.parent,self.length = parent, length
    class TargetRead: 
        def __init__(self, parent, length): self.parent,self.length = parent, length
    class SourceCopy: 
         def __init__(self, parent, length, relativeOffset): self.parent,self.length,self.relativeOffset = parent, length, relativeOffset
    class TargetCopy: 
        def __init__(self, parent, length, relativeOffset): self.parent,self.length,self.relativeOffset = parent, length, relativeOffset

    def __init__(self, patch : bytes):

        trim = lambda: patch[patch.index([byte for byte in patch[:16] if byte & 0x80][0])+1:]   #trim bps from first d0 enabled byte
        
        patch = patch[4:]
        self.source_size = decode(patch[:16]);patch = trim()     #Decode Source Size   | read 16 bytes ahead for u128i
        self.target_size = decode(patch[:16]);patch = trim()     #Decode Target Size   | read 16 bytes ahead for u128i
        self.metadata_size = decode(patch[:16]);patch = trim()   #Decode Metadata Size | read 16 bytes ahead for u128i
        
    
        self.metadata = patch[:self.metadata_size]             #Gather Metadata as bytearray (should be xml | may not be)
        patch = patch[self.metadata_size:]                    #trim bps to exclude metadata

        self.source_checksum = patch[-12:-8]
        self.target_checksum = patch[-8:-4]
        self.patch_checksum = patch[-4:]

        normalized = {}
         
        data_offset = 0
        while data_offset < len(patch):
            data = decode(patch[data_offset:])
            command = data & 3
            length = (data >> 2) + 1

            if command & 2:  # if command is 2 or 3, read relative_offset
                relative_offset = decode(patch[data_offset + 1:])
                data_offset += 2

            normalized[data_offset] = command, (length, data_offset) if command & 2 else (length,)
            data_offset += 1
        self.actions = [(self.SourceRead, self.TargetRead, self.SourceCopy, self.TargetRead)[action[0]](*action[1]) for action in normalized]

        





def apply(patch: bytes, source: bytes) -> bytes: 
    """
    Applies BPS Patch to source file
    """

    target = bytearray(source)
    source_checksum, target_checksum, patch_checksum = [patch[i:i+4] for i in range(-12, 0, 4)];patch = patch[4:-12]
    trim = lambda: patch[patch.index([byte for byte in patch[:16] if byte & 128][0])+1:]   #trim bps from first d0 enabled byte

    source_size = decode(patch[:16]); patch = trim()                    # Decode Source Size   | read 16 bytes ahead for u128i
    target_size = decode(patch[:16]); patch = trim()                    # Decode Target Size   | read 16 bytes ahead for u128i
    metadata_size = decode(patch[:16]); patch = trim()                  # Decode Metadata Size | read 16 bytes ahead for u128i

    if metadata_size:
        metadata = patch[:metadata_size];patch = patch[metadata_size:]  # Gather Metadata as bytearray (should be xml | may not be)


    def source_read() -> None:
        pass #nonlocal some variables and perform some function

    def target_read() -> None:
        pass #nonlocal some variables and perform some function


    def source_copy() -> None:
        pass #nonlocal some variables and perform some function

    def target_copy() -> None:
        pass #nonlocal some variables and perform some function

    #Here we shall haev the code to loop instructions

    return target, source_checksum, target_checksum, patch_checksum, metadata