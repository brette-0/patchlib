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
            
        def modify(self, operation : int = None, offset : int = None, length : int = None, payload : bytes = None, relative : int = None, name : str = None): 
            raise NotImplementedError("action modification is currently unimplemented")
            
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
    
    def range(self,start : int = 0, end : int = None, exclude_source_read : bool = False) -> bytes: 
        """
        Retrieves all existing actions within a specified range of offsets
        """

        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if start < 0: start = self.actions[-1].end+start 
        if end < 0: end = self.actions[-1].end+end
        if start > end : return [ins for ins in self.actions if (ins.end > start) and ((ins.operation) if exclude_source_read else True)]+[ins for ins in self.actions if (ins.end < end) and ((ins.operation) if exclude_source_read else True)]
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
        print(f"{offset} / {len(target)} | {len(patch)} / 352865 | {100-int(100*len(patch)/max(1, offset))}% | {len(str(round(length / (time.time()-slice_time if time.time()-slice_time else 1), 0)))} | {len(str(length))} | {(offset / len(target)) / (len(patch) / 352865)}")
        slice_time = time.time()
        
        """
        
        for performance reasons we must not perform iterative exponential array index evaluation
        apparently, this is horrible for efficiency. 
        
        We should only index, when we are confident that the data is not present at our current offset
        
        This code here should include any information that is not present in either files.
        target_read is the least efficient of all actions, the logic below is honestly unlikely
        to ever be required - but should it it is here.
        
        """
        length = 1
        if target[offset + length] not in target[:offset] and target[offset + length] not in source:
            while target[offset + length] not in source: length += 1
            length -= 1
            patch += encode(((length - 1) << 2) | 1) + target[offset : offset + length] 
            offset += length
            continue 
        
        """
        
        Here we have 64bit RLE detection, I can only imagine that this is what byuu used as I honestly
        cannot understand his code yet. What I have done here is move the logical evaluations into lambdas
        for readability, file size efficiency and concission. We divide with bitshifting to main integral values
        and we compare looped data against dividended slices with slice comparison. Finally we perform another
        slice comparison between the trailing bytes and the leading bytes of the loop.
        
        For true 64bit RLE this trailing factor is unimportant, HOWEVER, should it not impede on speed much
        it is a neat feature to implement. 
        
        """
        
        rle_lambda = lambda: target[offset : offset + ((length >> 2) * 4)] == target[offset : offset + 4] * (length >> 2) and target[offset + ((length >> 2) * 4) : offset + length] == target[offset : (length - ((length >> 2) * 4)) % 4]
        length = 1  
        
        if rle_lambda():
            while rle_lambda() and offset + length < len(target):
                length += 1
            length -= 1
            
        """
        
        In early versions of the code I had length equal zero. Which I had realized would initally
        create an empty byte array - thus leading to the loop suceeding every time. 
        Then entering a whole logical mess ... Not what I had in mind. 
        
        The value of the length may change in time.
        
        
        Naturally here is my solution: indexing if current compared offset does not equate to target
        with gradual slice comparison. The data compared is much lower, however more checks are 
        introduced this way. A compromise needed for this current level of hardware. 
        when the slice evaluation fails, this means the data we are comparing is too large for the
        evaluated offset. This failing allows us to garuntee we do not end up testing the data 
        we just used. 
        
        Finally, should no new index be viable - an IndexError will be thrown as we attempt
        to access data that simply does not exist. In which case we catch the error and break from our 
        loop. Should the final value of the offset added to the length exceed the length of data we have to
        access, then we may also need to exit the loop and perform a secondary check in order to ensure that we do 
        not use an undetermined terminator as that will keep us in an eternal loop.
        The value of the index is preserved and we now decrease the length by one to regain the length
        that succeeded the final loop.
        
        """  
        
        
        target_scope_lambda = lambda: target[offset : offset + length] == target[new_index : new_index + length]
        source_scope_lambda = lambda: target[offset : offset + length] == source[new_index : new_index + length]
        
        adder = 1
        
        if target[offset : offset + length] in target[:offset]:
            while True:
                try:
                    new_index = target[:offset].index(target[offset : offset + length])
                    while (target_scope_lambda()) if offset + length <= len(target) else False:
                        length <<= adder 
                        adder <<= 1
                except ValueError: break
                if offset + length > len(target): 
                    break
            while not target_scope_lambda() or length > len(target): 
                length >>= 1
                
            while target_scope_lambda():
                length += 1
                
            length -= 1
        
        target_length = length
        adder = 1
        
        if (target[offset : offset + length] in source) if length <= len(source) else False:
            while True:
                try:
                    new_index = source.index(target[offset : offset + length])
                    while (source_scope_lambda()) if length <= len(source) else False:
                        length <<= adder 
                        adder <<= 1
                except ValueError: break
                if offset + length > len(target): 
                    break
            while not source_scope_lambda() or length > len(source): 
                length >>= 1
                
            while source_scope_lambda():
                length += 1
                
            length -= 1
        
        source_length = length
        
        """
        
        now that we have got the lengths that we can achieve from target and source we must now begin
        the encoding process. Which is simpler but still has some layes of sophistication to it.
        
        """
        
        source_subsection_lambda = lambda: target[offset : offset + length] in source[max(source_relative - adder, 0) : min(source_relative + adder, len(source))]
        target_subsection_lambda = lambda: target[offset : offset + length] in target[max(target_relative - adder, 0) : min(target_relative + adder, len(target))]
        
        if source_length > target_length:
            if new_index == offset:
                patch += encode((length - 1) << 2)
                offset += length 
                continue
            
            adder = 1
            while not source_subsection_lambda():
                adder <<= 1
            
            relative = (source[max(source_relative - adder, 0) : min(source_relative + adder, len(source))].index(target[offset + length])) - (adder >> 1)
            action = encode(((length - 1) << 2) | 2) + encode(abs(relative << 1) | (relative < 0))
            if length > len(encode(abs(relative << 1) | (relative < 0))): 
                patch += action
                source_relative += relative + length 
            else:
                patch += encode(((length - 1) << 2) | 1) + target[offset : offset + length] 
            offset += length
            
        else: 
            adder = 1
            while not target_subsection_lambda():
                adder <<= 1
            relative = (target[max(target_relative - adder, 0) : min(target_relative + adder, len(target))].index(target[offset : offset + length])) - (adder >> 1)
            action = encode(((length - 1) << 2) | 2) + encode(abs(relative << 1) | (relative < 0))
            if length > len(encode(abs(relative << 1) | (relative < 0))): 
                patch += action
                target_relative += relative + length 
            else:
                patch += encode(((length - 1) << 2) | 1) + target[offset : offset + length] 
            offset += length
    
    print(time.time()-begin)
    patch += crc(source).to_bytes(4, "little") + crc(target).to_bytes(4, "little")              # add footer checksums
    return patch + crc(patch).to_bytes(4, "little")                                             # return patch with patch checksum
                                                    