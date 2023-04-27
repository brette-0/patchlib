"""
in-dev bps beta
"""

__version__ = "0.5"


from zlib import crc32

def encode(number : int, signed : bool = False) -> bytes:
    """
	Convert number into variable-width encoded bytes
    """

    if not isinstance(number,int): raise TypeError("Number data must be integer")
    if not isinstance(signed,bool): raise TypeError("sign flag must be boolean")
    if signed: number = abs(number * 2) + (number < 0)
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


def decode(encoded : bytes, signed : bool = False) -> int:
    """
	Decode variable-width encoded bytes into unsinged integer
    """
    if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")
    if not isinstance(signed,bool): raise TypeError("sign flag must be bool object")

    number = 0								    #Assume 0 for operational efficiency 
    shift = 1
    for byte in encoded:					    #for each byte in our given data
        number += (byte & 0x7f) * shift		    #increase number by data bits
        if byte & 0x80: break				    #break if termination bytes set
        shift <<= 7
        number += shift
    return (number>>1)*(-1 if number & 1 else 1) if signed else number							        #return decoded number

class bps:
    def __iter__(self): return iter(self.operations)
    def __getitem__(self, index): return self.operations[index]
    def __setitem__(self, index, value): self.operations[index] = value
    class operation:
        def __del__(self): 
            self.parent.remove(self)
        def __init__(self, parent, operation : int, length : int, outputOffset : int, **kwargs : dict):
            valid_kwargs = {"data", "relativeOffset", "name"}
            if not all(arg in valid_kwargs for arg in kwargs): raise ValueError(f"Invalid arguments provided: {set(kwargs.keys()) - valid_kwargs}")
            if not isinstance(length, int): raise TypeError("Length must be of type `int`")
            if length < 1: raise ValueError("length must be non-zero positive integer.")
            if not isinstance(outputOffset, int): raise TypeError("outputOffset must be of type `int`") 
            if outputOffset < 0: raise ValueError("outputOffset must be positive.")
            if not isinstance(operation,int): raise TypeError("instance indicator must of type `int`") 
            if abs(operation & 3) != operation: raise ValueError("operation indicator must be between 0 and 3")
            if kwargs.get("data") != None:
                if operation & 3 != 1: raise ValueError("`data` attribute only belongs to target_read action")                
                elif not isinstance(kwargs.get("data"), bytes): raise TypeError("`data` must be of type `bytes`") 
                elif not len(kwargs.get("data")): raise ValueError("`data` must be of non-zero length")     
            if kwargs.get("relativeOffset") != None:
                if not operation & 2: print(operation);raise ValueError("`relativeOffset` attribute only belongs to source_copy and target_copy actions") 
                elif not isinstance(kwargs.get("relativeOffset"),int): raise TypeError("`relativeOffset` must only be of type `int`") 
                #with nonlocal we may be able to access the actual offset.
            self.name = kwargs.get("name",f'Unnamed {("source_read","target_read","target_copy","target_read")[operation]} at {outputOffset}')
            self.__dict__.update({**{arg: data for arg, data in locals().items() if arg in {"parent","operation","length","outputOffset"}}, **kwargs})

    def __init__(self, patch : bytes, checks : bool = True):


        

        self.operations = [];outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None][::-1].hex() for i in range(-12, 0, 4)];patch = patch[:-4]


        if crc32(patch) != int(self.patch_checksum, 16) and checks:raise ValueError(f"Expected patch with checksum {hex(crc32(patch))[2:]} but calculated checksum of {self.patch_checksum}")
        patch = patch[4:-8]
        
        def trim(): nonlocal patch;patch = patch[patch.index([byte for byte in patch[:16] if byte & 128][0])+1:]#trim bps from first d0 enabled byte

        self.sourceSize = decode(patch[:16]);trim()                                # Decode Source Size   | read 16 bytes ahead for u128i
        self.targetSize = decode(patch[:16]);trim()                                # Decode Target Size   | read 16 bytes ahead for u128i
        self.metadataSize = decode(patch[:16]);trim()                              # Decode Metadata Size | read 16 bytes ahead for u128i


        if self.metadataSize:
            self.metadata = patch[:self.metadataSize];patch = patch[self.metadataSize:]     # Gather Metadata as bytearray (should be xml | may not be)


        while self.targetSize-outputOffset:                                                 # While there is still data subject to normalisation
            operation = decode(patch[:16]);trim()                                           # Decode operation  | read 16 bytes ahead for u128i
            operation,length = operation & 3,(operation >> 2) + 1                                                   # Determine length
            args = [self, length, outputOffset]                                             # Assume default args
            if operation & 2:                                                               # If a copy function (check this alot please NOT WORKING)
                relativeOffset = decode(patch[:16], True);trim()                            # Decode the modifier
                if operation & 1: targetRelativeOffset += relativeOffset                    # Modify Appropriate relativeOffset
                else: sourceRelativeOffset += relativeOffset
                args.append(targetRelativeOffset if operation & 1 else sourceRelativeOffset)# Add value to normalized data 
                self.operations.append(self.operation(self, operation & 3, length, outputOffset, relativeOffset = relativeOffset))
            elif operation & 1:                                                             # If target_read
                self.operations.append(self.operation(self, 1, length, outputOffset, data = patch[:length]));patch = patch[length:]                          # Append the actual data and trim patch accordingly
            else:
                self.operations.append(self.operation(self, 0, length, outputOffset))
            outputOffset += length                                                          # Increase variable counter to indicate 

            

    def remove(self, operation : operation) -> dict | tuple: 
        """
        This code will need to alter ALOT, we must assume source_read where possible, otherwise source_copy
        Any copy_codes will need their offset being changed in the following copy function to continue supprort.
        All lost patched will be returned in tuple or dict
        """
        return None

        

def apply(patch : bps, source : bytes, checks : bool = True) -> tuple:

    if not isinstance(patch, bps): raise ValueError() 
    if not isinstance(source, bytes): raise ValueError()
    if not isinstance(checks, bool): raise ValueError() 


    target = b"";sourceRelativeOffset = targetRelativeOffset = 0

    if len(source) != patch.sourceSize and checks: raise ValueError()
    if crc32(source) != patch.source_checksum and checks: raise ValueError()
    #patch corruption mechanic lost - but is that a bad thing entirely?
    if crc32(target) != patch.target_checksum and checks: raise ValueError() 
    if len(target) != patch.targetSize and checks: raise ValueError()   #potentially redudant?



    def source_read(operation : bps.operation): 
        nonlocal source, target
        if len(source[operation.outputOffset:operation.outputOffset + operation.length]) != operation.length: raise Exception("Fuck")
        target += source[operation.outputOffset:operation.outputOffset + operation.length]
    def target_read(operation : bps.operation): 
        nonlocal target
        if len(operation.data) != operation.length: raise Exception("Fuck")
        target += operation.data
    def source_copy(operation : bps.operation): 
        nonlocal source, target, sourceRelativeOffset
        sourceRelativeOffset += operation.relativeOffset
        if source[sourceRelativeOffset:sourceRelativeOffset+operation.lengt]: raise Exception("Fuck")
        target += source[sourceRelativeOffset:sourceRelativeOffset+operation.length]
    def target_copy(operation : bps.operation):
        nonlocal target, targetRelativeOffset
        targetRelativeOffset += operation.relativeOffset
        if len(source[sourceRelativeOffset:sourceRelativeOffset+operation.length]) != operation.length: raise Exception("Fuck")
        target += source[targetRelativeOffset:targetRelativeOffset+operation.length]


    for action in patch:
        (source_read,target_read,source_copy,target_copy)[action.operation](action)

    return (target, patch.metadata) if hasattr(patch, "metadata") else (target,)