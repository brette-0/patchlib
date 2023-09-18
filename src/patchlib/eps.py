"""
alpha eps by brette
"""

__version__ = "0.0"

#from patchlib.bps import encode

def encode(number : int) -> bytes:
    """enocdes numerical information with variable width encoding

    Args:
        number (int): the number to encode

    Returns:
        bytes: the encoded number
    """
    encoded = bytes()
    while True:
        x = number & 0x7f
        number >>= 7
        if number:
            encoded += x.to_bytes(1, "big")
            number -= 1
        else: return encoded + (0x80 | x).to_bytes(1, "big")

class eps:
    def instance(self, length : int, relative : int, name : str = None):
        self.length, self.relative, self.name = length, relative, name
        
    def __init__(self, source : bytes):
        if not source.startswith(b"EPS"): 
            raise ValueError("This file is not an EPS File!")
        else: eval(f"version_{source[3]}_init(self, source)")
        
    def version_0_init(self, patch): 
        """EPS (rev 0) initialisation code

        Args:
            patch (_type_): the raw patch file to normalize
        """
        def decode()->bytes: 
            nonlocal patch
            decoded, shift = 0, 1 
            while True:
                x = patch[0]
                patch = patch[1:]
                decoded += (x & 0x7f) * shift
                if x & 0x80: return decoded 
                shift <<= 7
                decoded += shift
            
        patch = patch[4:]
        bank_size = decode() 
        self.data_bank = patch[:bank_size] 
        patch = patch[bank_size:]
        self.instances = []
        offset = 0
        while len(patch):
            offset = decode()
            length = decode() 
            relative = decode()
            self.instances.append(self.instance(length, relative, False, f"Unnamed instance at {offset} with length {length}"))
            
def apply(source, patch : eps)-> bytes: 
    """applies an eps object to a source file
    
    Args:
        source (bytes): source file contents, the file the user has
        patch (eps): the eps object the user has normalized
        
    Returns:
        bytes: eps object patched file
    """
    offset = 0
    target = bytes()
    for instance in patch: 
        offset += instance.offset
        target += source[len(target):offset] + eps.data_bank[instance.relative : instance.relative + instance.length]
        offset += instance.length 
        
    return target
            

def build(source : bytes, target : bytes, version : int = 0) -> bytes:
    """builds an eps file from source and target contents

    Args:
        source (bytes): source file contents, the file the user has
        target (bytes): target file contents, the file the user does not have

    Returns:
        bytes: eps file raw contents
    """
    
    def version_0_build()->bytes:
        nonlocal source, target, version 
        data_bank = bytes()                     # init data bank 
        contents = bytes()                      # output contents
        offset = length = 0
        while source[offset + length] != target[offset + length]: length += 1 # not a flawless way to detect difference
        length -= 1
        if target[offset : length] not in data_bank: 
            end = True 
            while end:
                end = 0
                while target[offset : end] in data_bank and end >= (encode(offset) + encode(length) + encode(data_bank.index(target[offset : offset + end]))) and end < length:
                    end += 1
                if end:
                    contents += encode(offset) + encode(end) + encode(data_bank.index(target[offset : offset + end]))
                    offset += end
                else: 
                    start = 0
                    while start < length - end and target[offset + end + start : offset + length] in data_bank: 
                        start += 1
                    start -= 1
                    # index data bank for contents, and insert 
                    bank_pos = data_bank.index(target[offset + end + start : offset + length])
                    if data_bank[bank_pos - start: length - end].startswith(target[offset + end: offset + length]): 
                        pass # the data is leading
                    
        else:
            contents += encode(offset) + encode(length) + encode(data_bank.index(target[offset : offset + length]))
        offset += length
        """ 
        
        generate a slice
        split up for pre-existing contents
        #store pointers yaya
        
        """
        return b"EPS0" + data_bank + contents
    return eval(f"version_{version}_build()")