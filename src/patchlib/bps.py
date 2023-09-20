"""
in-dev bps beta
"""

class ChecksumMismatch(Exception): pass 
class ContinuityError(Exception): pass

#FOR DEV
import time

__version__ = "0.6"
from zlib import crc32 as crc 
import re
"""
def build   | build a BPS with : source, target | optional : metadata
def apply   | apply a BPS with : source         | optional : metadata, validate
"""

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
        
    def to_bytes(self, metadata : bool = False, checks : bool = True)->bytes:
        """process bps object into encoded file

        Args:
            metadata (bool, optional): metadata inclusion flag. Defaults to False.
            checks (bool, optional): validate checksums. Defaults to True.

        Returns:
            bytes: encoded bps file
        """
        contents = bytes() 
        for action in self: 
            contents += encode(((action.length - 1) << 2) + action.operation)
            if action.operation & 2: contents += encode(abs(action.relative * 2) + (action.relative < 0))
            elif action.operation & 1: contents += action.payload
        contents = b"BPS1"+ encode(self.source_size) + encode(self.target_size) + (encode(self.metadata_size if metadata else 0)) + (self.metadata if metadata and self.metadata_size else bytes()) + contents + int(self.source_checksum, 16).to_bytes(4, "little") + int(self.target_checksum, 16).to_bytes(4, "little")
        return contents + crc(contents).to_bytes(4, "little")
    #create(action : int, offset, payload, relative, name)
    def delete(self, action : source_read | target_read | relative_action)-> dict: 
        """delete an action from bps object.

        Args:
            action (action | source_read | target_read | relative_action): Action to be removed from bps object

        Returns:
            dict: Struct of deleted action attributes
        """
        store = {"parent" : action.parent, "length" : action.length, "offset" : action.offset, "name" : action.name}
        if isinstance(action, self.source_read): raise ContinuityError("Cannot delete empty space!") 
        if isinstance(action, self.target_read): 
            if isinstance(self.actions[self.actions.index(action)-1], self.source_read):
                store["payload"] = action.payload
                self.actions[self.actions.index(action)-1].length += action.length 
                self.actions.remove(action) 
            else: 
                temp = self.source_read(self, action.length, action.offset, f"Unnamed source read at {hex(action.offset)[2:].upper()} with length {hex(action.length)[2:].upper()}")
                self.actions.insert(self.actions.index(action), temp)
                self.actions.remove(action)
        if isinstance(action, self.relative_action): 
            store["relative"] = action.relative
            temp = [act for act in self.actions if act.operation == action.operation]
            if temp[-1] != action: 
                self.actions[self.index(temp.index(action) + 1)] -= action.relative
        return store
    
    def range(self,start : int = 0, end : int = None) -> bytes: 
        """
        Retrieves all existing actions within a specified range of offsets
        """

        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if start < 0: start = self.actions[-1].end+start 
        if end < 0: end = self.actions[-1].end+end
        if start > end : return [ins for ins in self.actions if ins.end > start]+[ins for ins in self.actions if ins.end < end]
        else: return [ins for ins in self.actions if ins.end > start and ins.offset < end] 
    
def apply(source : bytes, patch : bps, checks : bool = True, metadata : bool = False) -> tuple | bytes: 
    """apply a bps object to the required source file.

    Args:
        source (bytes): source file required by the patch
        patch (bps): patch object to be used on the source
        checks (bool, optional): perform checksum validation. Defaults to True.
        metadata (bool, optional): include metadata in output. Defaults to False.

    Raises:
        ChecksumMismatch: on source mismatch
        ChecksumMismatch: on target mismatch

    Returns:
        tuple | bytes: patched file, or combination of patched file with metadata
    """
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


def build(source : bytes, target : bps, metadata : bytes | bool = False) -> bytes:
    """build BPS patch from source and target file

    Args:
        source (bytes): file the user will have to create target
        target (bps): file the user will not have that will be made by this script
        metadata (bytes | bool, optional): metadata contents. Defaults to False.

    Returns:
        bytes: bps encoded file
    """
    begin = time.time()
    patch = b"BPS1" + encode(len(source)) + encode(len(target))                                 # Header
    if metadata and isinstance(metadata, bytes): patch += encode(len(metadata)) + metadata      # optional metadata
    else: patch += encode(0)                                                                    # else append terminated 0
    
    offset = length = source_relative = target_relative = 0
    adder = 1
    
    slice_time = 0
    while len(target) - offset: 
        print(f"{offset} / {len(target)} | {len(patch)} / 352865 | {100-int(100*len(patch)/max(1, offset))}% | {len(str(round(length / (time.time()-slice_time if time.time()-slice_time else 1), 0)))}")
        slice_time = time.time()
        
        # the logistical mess is entirely within the real of not file efficiency but TIMING.
        # the code takes HOURS TO COMPLETE. so we rewrite it again.
    
    print(time.time()-begin)
    patch += crc(source).to_bytes(4, "little") + crc(target).to_bytes(4, "little")              # add footer checksums
    return patch + crc(patch).to_bytes(4, "little")                                             # return patch with patch checksum
                                                    