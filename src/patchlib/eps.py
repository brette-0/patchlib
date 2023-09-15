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
    def instance(self, length : int, relative : int, copy : bool, name : str = None):
        self.length, self.relative, self.copy, self.name = length, relative, copy, name
        
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
            length = decode() 
            if length: 
                relative = decode()
                if relative & 1: 
                    relative = (relative >> 2) * (-1 if relative & 2 else 1) 
                    self.instances.append(self.instance(length, relative, True, f"Unnamed target copy at {offset} with length {length}"))
                else: 
                    relative >>= 1
                    self.instances.append(self.instance(length, relative, False, f"Unnamed data accesss at {offset} with length {length}"))
            else: 
                self.instances.append(self.instance(decode(), None, None, f"Unnamed source read at {offset} with length {length}"))
            offset += length
            
            
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
        
        """ 
        
        generate a slice
        identify overlap
        add loop contents to data_bank if not already present.
        set up target copy from there.
        
        #store pointers yaya
        
        """
        return b"EPS0" + data_bank + contents
    return eval(f"version_{version}_build()")