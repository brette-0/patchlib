"""
in-dev bps beta
"""

class ChecksumMismatch(Exception): pass 
class ContinuityError(Exception): pass

#FOR DEV
import time

__version__ = "0.6"
from zlib import crc32 as crc 

"""
def build   | build a BPS with : source, target | optional : metadata
def apply   | apply a BPS with : source         | optional : metadata, validate
"""

def encode(number : int, signed : bool = False) -> bytes:
                if signed: number = abs(number * 2) + (number < 0)
                encoded = bytes()
                while True:
                    x = number & 0x7f
                    number >>= 7
                    if number:
                        encoded += x.to_bytes(1, "big")
                        number -= 1
                    else: return encoded + (0x80 | x).to_bytes(1, "big")
                    
class bps:
    def __iter__(self): return iter(self.actions)
    def __getitem__(self, index): return self.actions[index]
    def __setitem__(self, index, value): self.actions[index] = value
    
    class action:
        def __init__(self, parent, operation : int, length : int, offset : int): 
            self.parent, self.operation, self.length, self.offset = parent, operation, length, offset
            self.end = offset + length
            
    class source_read(action):
        def __init__(self, parent, length : int, offset : int, name : str):
            super().__init__(parent, 0, length, offset)
            
            self.name = name
    class target_read(action):
        def __init__(self, parent, length : int, offset : int, name : str, payload : bytes):
            super().__init__(parent, 1, length, offset)
            self.name, self.payload = name, payload
            
    class relative_action(action):
        def __init__(self, parent, length : int, offset : int, name : str, relative : int, action : int):
            super().__init__(parent, action, length, offset)
            self.name, self.relative, self.source = name, relative, action & 1
            
    def __init__(self, patch : bytes, checks : bool = True, metadata : bool = True): 
        begin = time.time()
        self.source_checksum, self.target_checksum, self.patch_checksum = [patch[i:i+4 if i+4 else None][::-1].hex() for i in range(-12, 0, 4)]
        if checks and crc(patch[:-4]) != int(self.patch_checksum, 16): raise ChecksumMismatch("BPS file is corrupt!")
        patch = patch[4:-12]
        
        def decode():
            nonlocal patch
            decoded, shift = 0, 1 
            while True:
                x = patch[0]
                patch = patch[1:]
                decoded += (x & 0x7f) * shift
                if x & 0x80: return decoded 
                shift <<= 7
                decoded += shift
                
        self.source_size, self.target_size, self.metadata_size = decode(), decode(), decode()
        
        if metadata:
            self.metadata = bytes() 
            self.metadata_size = 0 
        else:
            self.metadata = patch[:self.metadata_size]
            patch = patch[self.metadata_size:]                
            
        self.actions = []
        offset = 0
        while patch:
            length = decode() 
            action  = length & 3
            length = (length >> 2) + 1 
            
            def add_source_read(): 
                nonlocal length, action, offset, patch
                self.actions.append(self.source_read(self, length, offset, f"Unnamed source read at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()}"))
            
            def add_target_read(): 
                nonlocal length, action, offset, patch
                payload = patch[:length]
                patch = patch[length:]
                self.actions.append(self.target_read(self, length, offset, f"Unnamed target read at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()}", payload))
            
            def add_relative_copy(): 
                nonlocal length, action, offset, patch
                relative = decode() 
                relative = (-1 if relative & 1 else 1) * (relative >> 1)
                self.actions.append(self.relative_action(self, length, offset, f"Unnamed {'target' if action & 1 else 'source'} copy at {hex(offset)[2:].upper()} with length {hex(length)[2:].upper()} and relative offset of {('-' if relative < 0 else '') + hex(relative)[2 + (relative < 0):].upper()}", relative, action))
            
            (add_source_read, add_target_read, add_relative_copy, add_relative_copy)[action]()
            offset += length
        if sum(tuple(action.length for action in self.actions)) != self.target_size:
            raise ContinuityError("BPS file is corrupt!")
        print(time.time() - begin)
        
    def to_bytes(self, metadata : bool = False, checks : bool = True):
        start = time.time()
        contents = bytes() 
        for action in self: 
            contents += encode(((action.length - 1) << 2) + action.operation)
            if action.operation & 2: contents += encode(action.relative, signed = True)
            elif action.operation & 1: contents += action.payload
        contents = b"BPS1"+ encode(self.source_size) + encode(self.target_size) + (encode(self.metadata_size if metadata else 0)) + (self.metadata if metadata and self.metadata_size else bytes()) + contents + int(self.source_checksum, 16).to_bytes(4, "little") + int(self.target_checksum, 16).to_bytes(4, "little")
        print(time.time()-start)
        return contents + crc(contents).to_bytes(4, "little")
    #create(action : int, offset, payload, relative, name)
    #delete(action : action)
    
    
def apply(source : bytes, patch : bps, checks : bool = True, metadata : bool = False) -> tuple | bytes: 
    target, source_relative_offset, target_relative_offset = bytes(), 0, 0
    if checks and crc(source) != int(patch.source_checksum, 16): raise ChecksumMismatch("Source File is not suited to this Patch!")
    for action in patch:
        if action.operation == 0:
            target += source[action.offset : action.end]
        if action.operation == 1:
            target += action.payload 
        if action.operation == 2:
            source_relative_offset += action.relative 
            target += source[source_relative_offset : source_relative_offset + action.length] 
            source_relative_offset += action.length
        if action.operation == 3:
            target_relative_offset += action.relative 
            if target_relative_offset + action.length < len(target):
                target += target[target_relative_offset: target_relative_offset + action.length]
            else:
                loop = target[target_relative_offset:]
                target += b"".join([loop for x in range(action.length // len(loop))]) + loop[:action.length % len(loop)]
            target_relative_offset += action.length
    if checks and crc(target) != int(patch.target_checksum, 16): raise ChecksumMismatch("Source File is not suited to this Patch!")
    return (target, patch.metadata) if patch.metadata_size and metadata else (target)


def build(source : bytes, target : bps, checks : bool = True, metadata : bytes | bool = False) -> bytes:
    patch = b"BPS1" + encode(len(source)) + encode(len(target))
    if metadata and isinstance(metadata, bytes): patch += encode(len(metadata)) + metadata 
    
    # likely a technical behemoth
    
    patch += crc(source).to_bytes(4, "little") + crc(target).to_bytes(4, "little")
    patch += crc(patch)
    
    return patch