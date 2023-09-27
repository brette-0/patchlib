"""
alpha eps by brette
"""

__version__ = "0.0"

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
            
        bank = decode()
        bank = patch[:bank] 
        pass 
    
    
    
    
def build(source : bytes, target : bytes) -> bytes:
    """_summary_

    Args:
        source (bytes): _description_
        target (bytes): _description_

    Returns:
        bytes: _description_
    """
    offset = pointer = adjustor = 0
    patch = bytes()
    
    if source == target: raise ValueError("Target cannoe be the same as source")
    while len(target) - offset:
        pass