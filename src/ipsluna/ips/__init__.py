class ScopeError(Exception): 
    """
    Raised when job scope exceeds limitations of IPS.
    """
    pass


class OffsetError(Exception): 
    """
    Raised when attepting to perform an illegal operation due to offset clashing
    """
    pass



class ips:
    class instance:

        def __del__(self):
            if self in self.parent.instances: self.parent.remove(self)

        def __init__(self, parent, offset : int, data : bytes | tuple, name : str = None):  

            """
            #add some documenting later
            """

            self.parent, self.rle,self.offset,self.data = parent, isinstance(data, tuple),offset,data 
            self.size = data[0] if self.rle else len(data)
            self.end = self.offset + self.size

            if name is None: self.name = f"unnamed instance at {offset} - {self.end} | {self.size}"
            else: self.name = name 


        def modify(self, **kwargs): 
            
            valid_args = {"offset", "data", "name", "overwrite", "sustain", "merge"}
            if not all(arg in valid_args for arg in kwargs):
                raise ValueError(f"Invalid arguments provided: {set(kwargs.keys()) - valid_args}")
    

            offset = kwargs.get("offset", self.offset)
            data = kwargs.get("data", self.data)
            name = kwargs.get("name", self.name)

            overwrite = kwargs.get("overwrite", False)
            sustain = kwargs.get("sustain", True)
            merge = kwargs.get("merge", False)

            self.parent.check_instance(offset, data, name, overwrite, sustain, merge)
            
            rle = isinstance(data, tuple) 
            #if merge and rle: data = data[0]*data[1]; rle = False
            size = data[0] if rle else len(data) 
            end = offset + size 

            clashes = list(self.parent.range(offset, end))
            if self in clashes: clashes.remove(self)

            if end > (0xFFFFFF if self.parent.legacy else 0x100FFFE): raise ScopeError("Target modification exceeds limitations of IPS")
            if end < 1: raise ScopeError("Target modification is below one and therefore impossible!")

            if len(clashes) == 1 and overwrite and sustain:
                if merge:  
                    temp = self.parent.remove(clashes[0])[0]                                                                                #obtain data from removal

                    if (temp["data"][1] != data[1]) if rle else True:
                       if temp["rle"]: temp["data"] = temp["data"][0]*temp["data"][1]
                       if rle: data = data[0]*data[1]; rle = False
                       data = temp["data"][:offset-temp["offset"]]+data+temp["data"][end-temp["offset"]:]
                    offset = temp["offset"]

                   
                else:
                    clash = clashes[0]
                    if clash.offset < offset: 
                        if clash.end > end:  
                            clash = self.parent.remove(clashes[0])[0]
                            self.parent.create(offset = clash["offset"], data = (
                                data[1] * (offset - clash["offset"]) if offset - clash["offset"] < 9 else (offset - clash["offset"],data[1])
                                ) if clash["rle"] else clash["data"][:offset - clash["offset"]]) 
                            self.parent.create(offset = end, data = (
                                data[1] * (end - clash["end"]) if end - clash["end"] < 9 else (end - clash["end"],data[1])
                                ) if clash["rle"] else clash["data"][end-clash["offset"]:])

                        else: clash.modify(data = (offset - clash.offset, clash.data[1]) if clash.rle else clash.data[:offset - clash.offset], name = None)
                    elif clash.end > end: clash.modify(offset = end,data = (clash.end - end, clash.data[1]) if clash.rle else clash.data[end-clash.offset:], name = None)


            elif len(clashes):
                if not overwrite: raise OffsetError("cannot modify instance due to clashing data!")  #come back to this laters 
            
                if sustain: 
                    if clashes[0].offset < offset: 
                        if merge: 
                            temp = self.parent.remove(clashes[0])[0]
                            if temp["rle"]: temp["data"] = temp["data"][0] * temp["data"][1] 
                            data = temp["data"] + data
                        else:
                            clashes[0].modify(data = (offset - clashes[0].offset, clashes[0].data[1]) if clashes[0].rle else clashes[0].data[:offset - clashes[0].offset], name = None)
                        clashes.pop(0)
                    if clashes[-1].end > end: 
                        if merge: 
                            temp = self.parent.remove(clashes[-1])[0]
                            if temp["rle"]: temp["data"] = temp["data"][0] * temp["data"][1] 
                            data = data + temp["data"]
                        else:
                            clashes[-1].modify(offset = end, data = (clashes[-1].end - end, clashes[-1].data[1]) if clashes[-1].rle else clashes[-1].data[end - clashes[-1].offset:],name = None)
                        clashes.pop(-1) 

                        
                for clash in clashes: self.parent.remove(clash) 

            self.data,self.rle,self.size,self.end = data,rle,size,end

            if offset != self.offset:
                self.offset = offset 
                self.parent.instances.remove(self)
                temp = self.parent.range(start = end)
                self.parent.instances.insert(self.parent.instances.index(temp[0]) if len(temp) else len(self.parent.instances),self)
            
            if name in {None, self.name}: self.name = f"unnamed instance at {offset} - {end} | {size}"
            else: self.name = name
    


    def check_instance(self, offset, data, name, overwrite, sustain, merge): 
        if not isinstance(name, str) and not name is None: raise TypeError("`name` must be type `string`")
        if not isinstance(offset, int): raise TypeError("`offset` must be type `int`")
        elif offset < 0: raise ScopeError("`offset` must be a positive integer") 
        elif offset > (0xFFFFFF if self.legacy else 0x100FFFE): raise ScopeError("`offset` must be within scope")
        if not isinstance(data, bytes):
            if isinstance(data, tuple):
                rle = True
                if not len(data) == 2: raise ValueError("`rle hunk` must contain only `length` and `data`")  
                if not isinstance(data[0],int): raise TypeError("`rle length` must be type `int`") 
                if not isinstance(data[1],bytes): raise TypeError("`rle data` must be type `bytes`") 
                if data[0] > 0xFFFF: raise ScopeError("`rle length` must be within scope!") 
                if data[0] < 1: raise ScopeError("`rle length` must be positive integer")
            else: raise TypeError("`data` must be type `bytes` or `tuple`")
        elif len(data) > 0xFFFF: raise ScopeError("`data` is impossibly large")
        else: rle = False 

        if offset + (data[0] if rle else len(data)) -1 > (0xFFFFFF if self.legacy else 0x100FFFE): raise ScopeError("instance attempts to write beyond possible scope")
        
        if not isinstance(name, str) and not name is None: raise TypeError("`name` must be type `str` or None")
        if not isinstance(overwrite, bool): raise TypeError("`overwrite` must be type `bool`")
        if not isinstance(sustain, bool): raise TypeError("`sustain` must be type `bool`")
        if not isinstance(merge, bool): raise TypeError("`merge` must be type `bool`")


    def __init__(self, patch : bytes, legacy : bool = True): 
        """
        add some documents later
        """
        
        if not isinstance(patch,(bytes, bytearray)): raise TypeError("normalized is not type `bytes` or `bytearray` and therefore cannot be accessed")
        if not isinstance(legacy, bool): raise TypeError("legacy flag must be either True or False")
        self.legacy = legacy

        try:
            if patch[:5]+patch[-3:] != b"PATCHEOF": raise Exception("Valid Header/Footer not Found!")
            count, changes,patch = 0, {}, patch[5:-3]
            while count != len(patch):
                count += 8
                if patch[count - 5] > 0 or patch[count - 4] > 0:
                    size = int(patch[count - 5:count - 3].hex(),16)
                    changes[int(patch[count-8:count - 5].hex(),16)] = patch[count - 3:count + size - 3]
                    count += size - 3
                else: changes[int(patch[count-8:count - 5].hex(),16)] = int(patch[count - 3:count - 1].hex(),16),bytes([patch[count - 1]]) 
        except Exception as InvalidIPS: raise OffsetError(f"Given file lacks integrity : {InvalidIPS}") from InvalidIPS 

        self.instances = [self.instance(self, offset, changes[offset]) for offset in changes]
        if legacy:
            badinstances = tuple(ins for ins in self.instances if ins.end > 0xFFFFFF)
            for ins in badinstances:
                print(f"{ins} >> will be destroyed due to legacy impossibility")
                self.remove(ins)

    
    def get(self, discriminator : str | int) -> instance | tuple: 
        
        """
        add some documents later
        """

        if not isinstance(discriminator, (str, int)): raise TypeError("`discriminator` must be type `str` or `int`") 

        finds = tuple(find for find in self.instances if discriminator in {find.offset, find.name})
        return finds if isinstance(discriminator, str) else (finds[0] if len(finds) else None)



    def create(self, offset : int, data : bytes | tuple, name : str = None, overwrite : bool = False, sustain : bool = True, merge : bool = False):  
        
        """ 
        """

        self.check_instance(offset, data, name, overwrite, sustain, merge)

        rle = isinstance(data, tuple) 
        size = data[0] if rle else len(data) 
        end = offset + size 
        name = f"unnamed instance at {offset} - {end} | {size}" if name is None else name

        clashes = list(self.range(offset, end))
         

        if len(clashes) == 1 and overwrite:
            clash = clashes[0]
            if clashes.offset < offset: 
                if clash.end > end:  
                    clash = self.remove(clashes[0])[0]
                    self.create(offset = clash["offset"], data = (offset - clash["offset"],clash["data"][1]) if clash["rle"] else clash["data"][:offset - clash["offset"]]) 
                    self.create(offset = end, data = (clash["end"]-end, clash["data"]-1) if clash["rle"] else clash["data"][clash["end"]-end:])
                    

                    """
                    removal with double creation may be faster than modification. we can experiment
                    later we can add checks for rle optimization
                    """
                else: clash.modify(data = (offset - clash.offset, clash.data[1]) if clash.rle else clash.data[:offset - clash.offset], name = None)
            elif clash.end > end: clash.modify(data = (clash.end - end, clash.data[1]) if clash.rle else clash.data[clash.end-end:], name = None)


        elif len(clashes): 
            if not overwrite: raise OffsetError("cannot modify instance due to clashing data!")  #come back to this laters 
            
            if sustain:
                if clashes[0].offset < offset: 
                    clashes[0].modify(data = (offset - clashes[0].offset, clashes[0].data[1]) if clashes[0].rle else clashes[0].data[:offset - clashes[0].offset], name = None)
                    clashes.pop(0)
                if clashes[-1].end > end: 
                    clashes[-1].modify(offset = end, data = (clashes[-1].end - end, clashes[-1].data[1]) if clashes[-1].rle else clashes[-1].data[clashes[-1].end - end:],name = None)
                    clashes.pop(-1)
            for clash in clashes: self.remove(clash) 


        temp = self.range(start = end)
        self.instances.insert(self.instances.index(temp[0]) if len(temp) else len(self.instances),self.instance(self, offset, data, name))
        
    
    def remove(self, discriminator : int | str | instance) -> dict | tuple: 
        
        if not isinstance(discriminator, (int, str, ips.instance)): raise TypeError("`discriminator` must be type `int`, `str` or `ips.instance`") 

        struct = ()
        if isinstance(discriminator, str): discriminator = self.get(discriminator)
        elif isinstance(discriminator, int): discriminator = (self.get(discriminator),)
        else: discriminator = (discriminator,)
        struct = []
        for find in discriminator:
            struct.append({element: getattr(find,element) for element in ("offset","data","rle","size","end","name")})
            self.instances.remove(find)

        return struct

        


    def range(self,start : int = 0, end : int = None) -> bytes: 
        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if end > 0xFFFFFF: raise ScopeError("`end` must be within possible scope") 
        if start > 0xFFFFFF: raise ScopeError("`start` must be within possible scope") 
        if start < 0: start = self.instances[-1].end+start 
        if end < 0: end = self.instances[-1].end+end
        if start > end : return [ins for ins in self.instances if ins.end > start]+[ins for ins in self.instances if ins.end < end]
        else: return [ins for ins in self.instances if ins.end > start and ins.offset < end]     

    def to_bytes(self) -> bytes:
        patch = b"" 
        for ins in self.instances:
            patch += ins.offset.to_bytes(3, "big")
            if ins.rle: patch += b"\x00\x00" 
            patch += ins.size.to_bytes(2, "big") 
            if ins.rle: patch += ins.data[1]
            else: patch += ins.data
        return b"PATCH"+patch+b"EOF"

    def __iter__(self) -> iter: return iter(self.instances)

    def __getitem__(self, index):
        return self.instances[index]

    def __setitem__(self, index, value):
        self.instances[index] = value

def build(base : bytes, target : bytes, legacy : bool = True) -> bytes: 

    if not isinstance(base, bytes): raise TypeError("`base` must be type `bytes`")  
    if not isinstance(target, bytes): raise TypeError("'target' must be type 'bytes'")  
    if not isinstance(legacy, bool): raise TypeError("'legacy' myst be type 'bool'")  

    if len(target) > (0xFFFFFF if legacy else 0x100FFFE): raise ScopeError("Target file exceeds IPS limitations!") 
    if len(base) > len(target): raise ScopeError("Target file must not be smaller than base file!")
    patch,count = b"", 0   

    viability = lambda offset, dist: target[offset].to_bytes(1, "big")*dist == target[offset : offset + dist]
    compare = lambda offset: (base[offset] != target[offset]) if offset < len(base) else True 

    def rle(): 
        length = 9
        while compare(count + length) and count + length < len(target) and viability(count, length): length += 1
        return length - 1

    def norle() : 
        length = 1 
        while compare(count + length) and count + length < len(target) and not (viability(count + length, 9) and all(compare(count + length + r) for r in range(9))): length += 1
        return length

    while count < len(target):
        if count == len(target)-1:
            patch += count.to_bytes(3, "big")+b"\x00\x01"+target[count].to_bytes(1, "big") 
            count += 1

        elif base[count] == target[count] if count < len(base) else target[count] == 0:
            while (base[count] == target[count] if count < len(base) else target[count] == 0) if count < len(target) - 1 else False: count += 1 

        else:
            isrle = viability(count, 9) and all(compare(count + r) for r in range(9)) 
            length = [norle,rle][isrle]()

            while length > 0xFFFF:
                if isrle: patch += count.to_bytes(3, "big")+b"\x00\x00\xff\xff"+target[count].to_bytes(1, "big") 
                else: patch += count.to_bytes(3, "big")+b"\xff\xff"+target[count:count+0xFFFF]
                count += 0xFFFF 
                length -= 0xFFFF

            if length:
                if isrle: patch += count.to_bytes(3, "big")+b"\x00\x00"+length.to_bytes(2, "big")+target[count].to_bytes(1, "big") 
                else: patch += count.to_bytes(3, "big")+length.to_bytes(2, "big")+target[count:count+length] 
                count += length

       
    return b"PATCH"+patch+b"EOF"

def apply(patch : ips, base : bytes) -> bytes:
        if not isinstance(patch, ips): raise TypeError("IPS given is not of type ips!")
        if not isinstance(base,bytes): raise TypeError("base given is not of type bytes or bytearray!")

        build = b""
        for instance in patch.instances: build+= (b"\x00" * (instance.offset - len(build)) if len(base) < instance.offset else base[len(build):instance.offset])+(instance.data[1]*instance.data[0] if instance.rle else instance.data)
        return build+ base[len(build):]