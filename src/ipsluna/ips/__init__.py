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
        def __init__(self, parent, offset : int, data : bytes | tuple, name : str = None):  

            """
            #add some documenting later
            """
            
            if not isinstance(data,(bytes,bytearray,tuple)): raise TypeError("Instance data is invalid!")
            if not len(data) ==  2 if isinstance(data,tuple) else False: raise ScopeError("Tuple has invalid data!")
            if not isinstance(offset, int): raise TypeError("Offset is not integral!")

            if offset > (0xFFFFFF if parent.legacy else 0x100FFFE): raise ScopeError("Offset exceeds limitations of IPS")
            if offset < 0: raise ScopeError("Offset is below zero and therefore impossible!")

            self.parent, self.rle,self.offset,self.data = parent, isinstance(data, tuple),offset,data 
            self.size = data[0] if self.rle else len(data)
            self.end = self.offset + self.size

            if name is None: self.name = f"unnamed instance at {offset} - {self.end} | {self.size}"
            elif isinstance(name, str): self.name = name 
            else: raise TypeError("Given name is not of type string and is therefore unsuitable")      


        def modify(self, **kwargs): 
            parent = self.parent                                                        #for readability 
            
            valid_args = {"offset", "data", "name", "overwrite", "sustain", "merge"}
            if not all(arg in valid_args for arg in kwargs):
                raise ValueError(f"Invalid arguments provided: {set(kwargs.keys()) - valid_args}")
    

            offset = kwargs.get("offset", self.offset)
            data = kwargs.get("data", self.data)
            name = kwargs.get("name", self.name)

            size = data[0] if isinstance(data, tuple) else len(data)

            if not isinstance(offset, int): raise TypeError("Offset must be integer")
            if not isinstance(data, (bytes, bytearray, tuple)): raise TypeError("data must be `bytes`, `bytearray` or `tuple` object.")
            if not isinstance(name, str) and not name is None: raise TypeError("name must be string") 

            if not len(data) ==  2 if isinstance(data,tuple) else False: raise ScopeError("Tuple has invalid data!")
            if offset > (0xFFFFFF if parent.legacy else 0x100FFFE): raise ScopeError("Offset exceeds limitations of IPS")
            if offset < 0: raise ScopeError("Offset is below zero and therefore impossible!")


            overwrite = kwargs.get("overwrite", False)
            sustain = kwargs.get("sustain", True)
            merge = kwargs.get("merge", False)

            
            rle = isinstance(data, tuple) 
            size = data[0] if rle else len(data) 
            end = offset + size 

            clashes = list(parent.range(offset, end))
            if self in clashes: clashes.remove(self)

            if len(clashes) == 1 and overwrite:
                clash = clashes[0]
                if clash.offset < offset: 
                    if clash.end > end:  
                        clash = parent.remove(clashes[0])
                        parent.create(offset = clash["offset"], data = (offset - clash["offset"],clash["data"][1]) if clash["rle"] else clash["data"][:offset - clash["offset"]]) 
                        parent.create(offset = end, data = (clash["end"]-end, clash["data"]-1) if clash["rle"] else clash["data"][clash["end"]-end:])
                    

                        """
                    removal with double creation may be faster than modification. we can experiment
                    later we can add checks for rle optimization
                        """
                    else: clash.modify(data = (offset - clash.offset, clash.data[1]) if clash.rle else clash.data[:offset - clash.offset], name = None)
                elif clash.end > end: clash.modify(offset = end,data = (clash.end - end, clash.data[1]) if clash.rle else clash.data[clash.end-end:], name = None)


            elif len(clashes):
                if not overwrite: raise OffsetError("cannot modify instance due to clashing data!")  #come back to this laters 
            
                if sustain:
                    if clashes[0].offset < offset: 
                        clashes[0].modify(data = (offset - clashes[0].offset, clashes[0].data[1]) if clashes[0].rle else clashes[0].data[:offset - clashes[0].offset], name = None)
                        clashes.pop(0)
                    if clashes[-1].end > end: 
                        clashes[-1].modify(offset = end, data = (clashes[-1].end - end, clashes[-1].data[1]) if clashes[-1].rle else clashes[-1].data[end - clashes[-1].offset:],name = None)
                        clashes.pop(-1)
                for clash in clashes: parent.remove(clash) 

            self.data = data 
            self.rle = rle
            self.size = size
            self.end = end

            if "offset" in kwargs.keys():
                self.offset = offset 
                parent.instances.remove(self)
                temp = parent.range(start = end)
                parent.instances.insert(parent.instances.index(temp[0]) if len(temp) else len(parent.instances),self)

            if name in {None, self.name}:  
                self.name = f"unnamed instance at {offset} - {end} | {size}"
            

    def __init__(self, patch : bytes, legacy : bool = True): 
        
        """
        add some documents later
        """
        self.legacy = legacy
        if not isinstance(patch,(bytes, bytearray)): raise TypeError("normalized is not type `bytes` or `bytearray` and therefore cannot be accessed")
        if not isinstance(legacy, bool): raise TypeError("legacy flag must be either True or False")

        try:
            count, changes,patch = 0, {}, patch[5:-3]
            while count != len(patch):
                count += 8
                if patch[count - 5] > 0 or patch[count - 4] > 0:
                    size = int(patch[count - 5:count - 3].hex(),16)
                    changes[int(patch[count-8:count - 5].hex(),16)] = patch[count - 3:count + size - 3]
                    count += size - 3
                else:  #Handle RLE, only if NON-RLE is not met     
                    changes[int(patch[count-8:count - 5].hex(),16)] = int(patch[count - 3:count - 1].hex(),16),bytes([patch[count - 1]]) 


        except IndexError as InvalidIPS: 
            raise Exception(f"Given file lacks integrity : {InvalidIPS}") from InvalidIPS   #!!!! FIX LATER, VERY BAD

        self.instances = [self.instance(self, offset, changes[offset]) for offset in changes]

        if legacy:
            badinstances = [ins for ins in self.instances if ins.end > 0xFFFFFF]
            for ins in badinstances:
                print(f"{ins} >> will be destroyed due to legacy impossibility")
                self.remove(ins)
    
    def get(self, discriminator : str | int) -> instance | tuple: 
        
        """
        add some documents later
        """

        if not isinstance(discriminator, (str, int)): raise TypeError("`discriminator` must be type `str` or `int`") 

        finds = [find for find in self.instances if discriminator in {find.offset, find.name}]
        return finds if isinstance(discriminator, str) else (finds[0] if len(finds) else None)



    def create(self, offset : int, data : bytes | tuple, name : str = None, overwrite : bool = False, sustain : bool = True, merge : bool = False):  
        
        """ 
        """


        if not isinstance(offset, int): raise TypeError("`offset` must be type `int`")
        if not isinstance(data, bytes):
            if isinstance(data, tuple):
                if not len(data) == 2:
                    raise ValueError("`rle hunk` must contain only `length` and `data`")  
                if not isinstance(data[0],int): raise TypeError("`rle length` must be type `int`") 
                if not isinstance(data[1],bytes): raise TypeError("`rle data` must be type `bytes`") 
                if data[0] > (0xFFFFFF if self.legacy else 0x100FFFE): raise ScopeError("`rle length` must be within scope!") 
                if data[0] < 0: raise ScopeError("`rle length` must be positive integer")
            else: raise TypeError("`rle hunk` must be type `tuple`")
        
        if not isinstance(name, str) and not name is None: raise TypeError("`name` must be type `str`")
        if not isinstance(overwrite, bool): raise TypeError("`overwrite` must be type `bool`")
        if not isinstance(sustain, bool): raise TypeError("`sustain` must be type `bool`")
        if not isinstance(merge, bool): raise TypeError("`merge` must be type `bool`")

        rle = isinstance(data, tuple) 
        size = data[0] if rle else len(data) 
        end = offset + size 
        name = f"unnamed instance at {offset} - {end} | {size}"

        clashes = list(self.range(offset, end))
         

        if len(clashes) == 1 and overwrite:
            clash = clashes[0]
            if clashes.offset < offset: 
                if clash.end > end:  
                    clash = self.remove(clashes[0])
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
        

    def remove(self, ins : int | str | instance) -> dict | tuple: 
        #add necessary checks
        struct = ()
        if isinstance(ins, str):
            ins = self.get(ins)
        if isinstance(ins, int):
            ins = [self.get(ins)] 
        if isinstance(ins, self.instance): 
            ins = [ins]
        for find in ins:
            struct = []
            if find in self.instances: 
                struct.append({element: getattr(find,element) for element in ("offset","data","rle","size","end","name")})
                self.instances.remove(find)
                del find 

        if len(struct) > 1:
            return (tree for tree in struct) 
        elif len(struct): return struct[0]
        else: return None

        


    def range(self,start : int = 0, end : int = None): 
        if end is None: end = 0xFFFFFF
        if not isinstance(start, int): raise TypeError("`start` must be of type `int`")
        if not isinstance(end, int): raise TypeError("`end` must be of type `int`")
        if end > 0xFFFFFF: raise ScopeError("`end` must be within possible scope") 
        if start > 0xFFFFFF: raise ScopeError("`start` must be within possible scope") 
        if start > end : raise ValueError("`end` must be higher than `start`") 


        """
        perhaps I may add wrap around
        """
        return [ins for ins in self.instances if ins.end > start and ins.offset < end] 




def make(base : bytes | bytearray, modded : bytes | bytearray, legacy : bool = True, legal : bool = None) -> bytes:

    #make it create `ips` class
    if len(modded) > (0xFFFFFF if legacy else 0x100FFFE): raise Exception("Scope impossible")
    ipsf,count = b"",0
    while count != len(modded):
        data = 0
		
		#The 5 is crucial for rle viability checks with optimization
        if count  + 5 < len(base) and legal:
		#do not add matches ever
		
            while base[count] is modded[count]:
                count += 1
				
			#if we can't find a match in the next 5 bytes, prefer rle
            if True not in [base[x] is modded[x] for x in range(5)] and bytes(modded[count])*5 is modded[count:count+5]:
				
				#check consecutive bytes
                while modded[count + data] is modded[count] if len(base) > count + data + 1 else True:
                    data += 1
                data = (data//0xFFFF,data%0xFFFF)
                for split in range(data[0]):
                    ipsf += count.to_bytes(3,"big")+b"\x00\x00\xff\xff"+bytes([count])
                    count += 0xFFFF
                ipsf += count.to_bytes(3,"big")+data[1].to_bytes(2,"big")+bytes([count])
                count += data[1].to_bytes
				
					
					
				
            else:
                    #for each failed match
                    while not base[count] is modded[count] if len(base) > count + data + 1 else True:
                        if bytes([modded[count + data]])*5 is modded[count:count+data+5]: break 
                        data += 1
                    data = data // 0xFFFF, data % 0xFFFF

                    for split in range(data[0]):
                        ipsf += count.to_bytes(3, "big")+b"\xff\xff"+modded[count:count+0xFFFF] 
                        count += 0xFFFF 
                    ipsf += count.to_bytes(3, "big")+data[1].to_bytes(2,"big")+modded[count:count+data[1]] 
                    count += data[1]
				    


				

				
				
        else:
			#do not append zerodata
            while not modded[count]:
                count += 1

			#is rle viable/possible form this offset
            if bytes([modded[count]])*5 is count[count:count+5]:
                while modded[count + data] is modded[count]:
                    data += 1
                data = (data//0xFFFF,data%0xFFFF)
                for split in range(data[0]):
                    ipsf += count.to_bytes(3,"big")+b"\x00\x00\xff\xff"+bytes([count])
                    count += 0xFFFF
                ipsf += count.to_bytes(3,"big")+data[1].to_bytes(2,"big")+bytes([count])
                count += data[1].to_bytes
				
			#granted rle is unviable, check for viability throughout constructor
            else:
                while not bytes([modded[count]])*5 is count[count:count+5]:
                    data += 1

                data = data // 0xFFFF, data % 0xFFFF

                for split in range(data[0]):
                    ipsf += count.to_bytes(3, "big")+b"\xff\xff"+modded[count:count+0xFFFF] 
                    count += 0xFFFF 
                ipsf += count.to_bytes(3, "big")+data[1].to_bytes(2,"big")+modded[count:count+data[1]] 
                count += data[1]

        if count is len(modded)-1:
            ipsf += count.to_bytes(3,"big")+b"\x00\x00\x00\x01\x00"
    return ips(ipsf)

def apply(patch : ips, base : bytes | bytearray) -> bytes:
        """
        document later
        """

        if not isinstance(patch, ips): raise TypeError("IPS given is not of type ips!")
        if not isinstance(base,(bytes,bytearray)): raise TypeError("base given is not of type bytes or bytearray!")

        build = b""
        for instance in patch.instances: build+= (b"\x00" * (instance.offset - len(build)) if len(base) < instance.offset else base[len(build):instance.offset])+(instance.data[1]*instance.data[0] if instance.rle else instance.data)
        return build+ base[len(build):]


        """
        if len(base) > instance.offset                         #If still overwriting
            build+= base[len(build):instance.offset]            #store original data up to this current point
            else:                                                  #otherwise we are appending new bytes
                build+= b"\x00" * (instance.offset - len(build))    #and therefore will append zerodata until the first offset
            if instance.rle:                                       #if instance is of type rle
                build+= instance.data[1]*instance.data[0]           #append bytes of hunk byte with hunk length | byte : length
        """