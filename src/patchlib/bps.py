"""
in-dev bps beta
"""

class ChecksumMismatch(Exception): pass 


__version__ = "0.5"


from zlib import crc32

def encode(number : int, signed : bool = False) -> bytes:
    """
	Convert number into variable-width encoded bytes
    """

    if not isinstance(number,int): raise TypeError("Number data must be integer")
    if not isinstance(signed,bool): raise TypeError("sign flag must be boolean")
    if not signed: signed = number < 0          # Determine signature if not set
    if signed: number = abs(number * 2) + (number < 0)
	
    var_length = bytes()						# Create empty bytes object to store variable-width encoded bytes
    while True:									# Until we are finished
        x = number & 0x7f						# Using the 7 LSB of the number
        number >>= 7							# And removing the data
        if number: 								# If there is still source data to read
            var_length += x.to_bytes(1, "big")	# Append the data to our bytes object
            number -= 1							# Decrement by one to remove ambiguity
        else: 
            var_length += (0x80 | x).to_bytes(1, "big")	# Set termination byte
            return var_length                   # Final data is wronte, leave


def decode(encoded : bytes, signed : bool = False) -> int:
    """
	Decode variable-width encoded bytes into unsinged integer
    """
    if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")
    if not isinstance(signed,bool): raise TypeError("sign flag must be bool object")

    number, shift = 0, 1                        #Assume 0 for operational efficiency 
    for byte in encoded:					    #for each byte in our given data
        number += (byte & 0x7f) * shift		    #increase number by data bits
        if byte & 0x80: return (number>>1)*(-1 if number & 1 else 1) if signed else number				    #break if termination bytes set
        shift <<= 7
        number += shift


class bps:
    """
    Normalised BPS patch object
    """
    def __iter__(self): return iter(self.operations)
    def __getitem__(self, index): return self.operations[index]
    def __setitem__(self, index, value): self.operations[index] = value
    class operation:
        """
        Singular BPS patch operation object
        """
        def __del__(self): 
            self.parent.remove(self)
        def __init__(self, parent, operation : int, length : int, outputOffset : int, **kwargs : dict):
            valid_kwargs = {"data", "relativeOffset", "name"}   #Needed for fstring compatibility
            if not all(arg in valid_kwargs for arg in valid_kwargs):              #Invalid kwarguements being raise
                raise ValueError(f"Invalid arguments provided: {set(kwargs.keys()) - valid_kwargs}")
            
            
            """
            Validates by object size and type. 
            """
            if not isinstance(parent, bps): raise TypeError("operation must originate from bps")
            if not isinstance(length, int): raise TypeError("Length must be of type `int`")
            if not isinstance(outputOffset, int): raise TypeError("outputOffset must be of type `int`") 
            if not isinstance(operation,int): raise TypeError("instance indicator must of type `int`")
            if length < 1: raise ValueError("length must be non-zero positive integer.")
            if outputOffset < 0: raise ValueError("outputOffset must be positive.")
            if abs(operation & 3) != operation: raise ValueError("operation indicator must be between 0 and 3") #Counters negative numbers and allows 0-3 range :0
            
            if kwargs.get("data") != None:  #checks for target_read
                if operation - 1: raise ValueError("`data` attribute only belongs to target_read action")                
                elif not isinstance(kwargs.get("data"), bytes): raise TypeError("`data` must be of type `bytes`") 
                elif not len(kwargs.get("data")): raise ValueError("`data` must be of non-zero length")    

            if kwargs.get("relativeOffset") != None:
                if not operation & 2: raise ValueError("`relativeOffset` attribute only belongs to source_copy and target_copy actions") 
                elif not isinstance(kwargs.get("relativeOffset"),int): raise TypeError("`relativeOffset` must only be of type `int`") 
                #with nonlocal we may be able to access the current value of relativeOffset.

            self.name = kwargs.get("name",f'Unnamed {("source_read","target_read","target_copy","target_read")[operation]} at {outputOffset}')          #evaluate name
            self.__dict__.update({**{arg: data for arg, data in locals().items() if arg in {"parent","operation","length","outputOffset"}}, **kwargs})  #attribute by pos arg, and kwarg

    def __init__(self, patch : bytes, checks : bool = True, metadata : bool = True):
        self.operations = [];outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None][::-1].hex() for i in range(-12, 0, 4)]


        # Calculate checksum of encoded contents
        if crc32(patch[:-4]) != int(self.patch_checksum, 16) and checks:raise ChecksumMismatch(f"Expected patch with checksum {hex(crc32(patch[:-4]))[2:]} but calculated checksum of {self.patch_checksum}")
        patch = patch[4:-12]
        
        def trim(): #trim bps from first d0 enabled byte
            nonlocal patch 
            temp = [byte for byte in patch[:16] if byte & 128]  
            patch = patch[patch.index(temp[0])+1:] if patch else bytes()

        # Acess all crucial metadata
        self.sourceSize = decode(patch[:16]);trim()                                # Decode Source Size   | read 16 bytes ahead for u128i
        self.targetSize = decode(patch[:16]);trim()                                # Decode Target Size   | read 16 bytes ahead for u128i
        self.metadataSize = decode(patch[:16]) if metadata else 0;trim()           # Decode Metadata Size | read 16 bytes ahead for u128i
        if self.metadataSize and metadata: self.metadata = patch[:self.metadataSize];patch = patch[self.metadataSize:]     # Gather Metadata as bytearray (should be xml | may not be)

        # while some of the patch is uninterpreted
        while self.targetSize-outputOffset:                                                 # While there is still data subject to normalisation
            operation = decode(patch[:16]);trim()                                           # Decode operation  | read 16 bytes ahead for u128i
            operation,length = operation & 3,(operation >> 2) + 1                           # Determine length
            if operation & 2:                                                               # If a copy function (check this alot please NOT WORKING)
                relativeOffset = decode(patch[:16], True);trim()                            # Decode the modifier
                if operation & 1: targetRelativeOffset += relativeOffset                    # Modify Appropriate relativeOffset
                else: sourceRelativeOffset += relativeOffset
                if targetRelativeOffset > outputOffset: raise Exception(outputOffset)       # Is never raised
            self.operations.append(self.operation(self, operation, length, outputOffset, 
                                                  relativeOffset = relativeOffset if operation & 2 else None, 
                                                  data = patch[:length] if operation == 1 else None))
            if operation & 3 == 1: patch = patch[length:]
            outputOffset += length                                                          # Increase variable counter to indicate 

    def to_bytes(self, source : bytes = None, checks : bool = False, metadata : bool = True) -> bytes:
        """
        Processes BPS object into raw BPS file
        """
        #metadata is a flag for including it in conversion or not
        #use sourceSize and checksum, this would also determine target (perhaps the result on last-modification can be stored in self?)
        raw = b"BPS1"
        for item in (self.sourceSize,self.targetSize,self.metadataSize if metadata else 0): 
            raw += encode(item, signed = False) 
        if self.metadataSize and metadata: raw += self.metadata 
        for oper in self:
            raw += encode(((oper.length -1) << 2) + oper.operation)
            if oper.operation & 2:
                raw += encode(oper.relativeOffset, signed = True) 
            elif oper.operation & 1:
                raw += oper.data 
        for item in (crc32(source),crc32(self.apply(self, source))) if source else (self.source_checksum,self.target_checksum):
            raw += int(item,16).to_bytes(4, "little")
        return raw+crc32(raw).to_bytes(4, "little")

    def remove(self, operation : operation) -> dict | tuple: 
        """
        This code will need to alter ALOT, we must assume source_read where possible, otherwise source_copy
        Any copy_codes will need their offset being changed in the following copy function to continue supprort.
        All lost patched will be returned in tuple or dict
        """
        return None
    
    def get(self, discriminator : str | int, operationtype : int | str = None, relative : int = None):
        if not isinstance(discriminator, (str, int)):
            raise TypeError("`discriminator` must be type `str` or `int`")
        if operationtype != None: 
            if isinstance(operationtype, int):
                if operationtype > 3: raise ValueError("`operationtype` cannot be greater than 3")
                elif operationtype < 0: raise ValueError("`operationtype` cannot be less than 0")
            try: 
                operationtype = ("source_read","target_read","target_copy","target_read").index(operationtype)
            except IndexError:
                raise ValueError("Invalid `operationtype` name.")
            if relative != None and not operationtype & 0x2: raise ValueError("Specified Operation Type does not have relative offset property")
        
        target = [oper for oper in self.operations if (True if operationtype == None else oper.operation == operationtype)]
        hasrel = "(discriminator in {oper.offset, oper.name} or relative == oper.RelativeOffset)"
        no_rel = "discriminator in {oper.offset, oper.name}"
        return [oper for oper in target if eval(no_rel, hasrel)[relative]]
         
         
    def range(self,start : int = 0, end : int = None) -> bytes: 
        """
        Retrieves all existing instances within a specified range of offsets
        """

        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if start < 0: start = self.operations[-1].end+start 
        if end < 0: end = self.operations[-1].end+end
        if start > end : return [ins for ins in self.operations if ins.end > start]+[ins for ins in self.operations if ins.end < end]
        else: return [ins for ins in self.operations if ins.end > start and ins.offset < end]     

    def __iter__(self) -> iter: return iter(self.operations)

    def __getitem__(self, index):
        return self.operations[index]

    def __setitem__(self, index, value):
        self.operations[index] = value

        

def apply(patch : bps, source : bytes, checks : bool = True, metadata : True = False) -> bytes | tuple:
    """
    Applies BPS object to provided source file
    """

    if not isinstance(patch, bps): raise ValueError("Patch must be normalized `bps` object") 
    if not isinstance(source, bytes): raise ValueError("Source must be `bytes` object")
    if not isinstance(checks, bool): raise ValueError("Checks flag must be set to boolean value") 
    if not isinstance(metadata, bool): raise ValueError("metadata flag must be set to boolean value") 

    if len(source) != patch.sourceSize and checks: raise ValueError(f"Expected source with size {patch.sourceSize} but calculated checksum of {len(source)}")
    if crc32(source) != patch.source_checksum and checks: raise ChecksumMismatch(f"Expected source with checksum {patch.source_checksum} but calculated checksum of {crc32(source)}")

    target = bytes();sourceRelativeOffset = targetRelativeOffset = 0

    debug_count = 0

    for action in patch: 
        if action.operation == 3:
            targetRelativeOffset += action.relativeOffset 
            if targetRelativeOffset+action.length >= len(target)-1: raise Exception("we messed up")
            target += target[targetRelativeOffset:targetRelativeOffset+action.length]   #this code not work at all the length flaw was found here
            debug_count += len(target[targetRelativeOffset:targetRelativeOffset+action.length])
        elif action.operation == 2:
            sourceRelativeOffset += action.relativeOffset 
            target += source[sourceRelativeOffset:sourceRelativeOffset+action.length]
            debug_count += action.length
        elif action.operation == 1: target += action.data ; debug_count += len(action.data)
        else: target += source[action.outputOffset:action.outputOffset+action.length]; debug_count += len(source[action.outputOffset:action.outputOffset+action.length])

    print(debug_count)

    if patch[-1].outputOffset + patch[-1].length != patch.targetSize and checks: raise ValueError(f"Expected target with size {patch.targetSize} but discovered file with size {len(target)}")
    if crc32(source) != patch.source_checksum and checks: 
        raise ChecksumMismatch(f"Expected source with checksum {patch.source_checksum} but calculated checksum of {crc32(source)}")
    return ((target, patch.metadata) if hasattr(patch, "metadata") else (target,)) if metadata else target



def build(source : bytes, target : bytes, metadata : bytes = bytes()): pass