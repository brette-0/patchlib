class OffsetError(Exception):
    """
    Raised when attepting to perform an illegal operation due to offset clashing
    """
    pass

class ScopeError(Exception):
    """
    Raised when job scope exceeds limitations of IPS.
    """


    
        
        

class ips:
    class instance:
        """
        Task stored in ips file storing data for modification. 
        """
        def __init__(self, offset : int,data : bytes | bytearray | tuple,name : str = None):
            """
            IPS instance initialization 
            :param int offset: Offset for where the patcher will write to
            :param str name: The secondary key "name" used to provide more human information on the instance.
            :param data: The integrity of the IPS 
            :type data: bytes or bytearray or tuple
            :raises TypeError: if offset is not integral
            :raises TypeError: if name is not string or None
            :raises ScopeError: if offset is above 0xFFFFFF or smaller than zero.
            """
            if not isinstance(data,(bytes,bytearray,tuple)): raise TypeError("Instance data is invalid!")
            if not len(data) is 2 if isinstance(data,tuple) else False: raise ScopeError("Tuple has invalid data!")
            if not isinstance(offset, int): raise TypeError("Offset is not integral!")
            if offset > min(0xFFFFFF, (2**super().bitsize)-1): raise ScopeError("Offset exceeds limitations of IPS")
            if offset < 0: raise ScopeError("Offset is below zero and therefore impossible!")
            if name is None: self.name = f"Unamed patch at {offset}"
            elif isinstance(name, str): self.name = name 
            else: raise TypeError("Given name is not of type string and is therefore unsuitable")
            self.rle,self.offset,self.data = isinstance(data, tuple),offset,data 
            self.size = data[1] if self.rle else len(data)
            self.end = self.offset + self.size


        def modify(self, offset : int = None, data : bytes | bytearray | tuple = None, name : str = None, override : bool = False, sustain : bool = True):
            jobs = [attr for attr in ["offset", "data", "name"] if not eval(attr) is None]  #gather a list of all modification
            if not len(jobs): raise Exception("No jobs given :/")               #if there is nothing to do then raise exception

            if self.name != name and not name is None:                              #if attempting re-name
                if isinstance(name,str): self.name = name                           #if legal, perform
                else: raise TypeError("Given name is not suitable as it is not str")#else raise TypeError

            for resolve in jobs:                                                    #of all jobs to do
                if eval(resolve) is None: eval(f"{resolve} = self.{resolve}")       #define locals by equal attributes

            clashes = super().in_range(end=offset)[0],super().in_range(offset, offset+(data[1] if isinstance(data,tuple) else len(data))) 
            #retrieve all instances of the parent class from the start of the offset to the end
            if len(clashes):    #if not zero-length
                if override:    #if override flag set
                    for ins in clashes:super().remove(ins)  #for each instance in parent, remove
                else: raise ScopeError("Space is already occupied by other instances")  #otherwise raise ScopeError due to impossible task
            self.offset, self.data,self.name = offset, data, self.name if name is None else name   #gathered that no errors rose, finish the data
            self.rle = isinstance(self.data,tuple)
            #could we just do self.__init__(self, offset, data, name)?      
             
            super().instances.remove(self)                                                      #remove
            temp = super().instances.index(super().in_range(self.offset)[0])                    #from start = self.offset, end = (2**super().bitsize)-1 DEF
            super().instances.insert(temp,self)                                                 #update

            #If offset has been modified, we need to retrieve the super().instances index of the upper consecutive offset. We use in_range?
            #instance needs to chronologicaly tranpose as well as mathamatically.

    def __init__(self, patch : bytes | bytearray, bitsize : int = 24):
        """
        initialization maps out all instances in normalized dictionary into `instances`
        :raises TypeError: if normalized is not type `dict`
        """

        if not isinstance(changes,dict): raise TypeError("normalized is not type `dict` and therefore cannot be accessed")
        if not isinstance(bitsize, (bytes | bytearray)): raise TypeError("specified bitsize is not type `int`")
        if bitsize % 8 or not bitsize: raise ScopeError("specified bitsize impossible")


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


        except AttributeError as invalidData: pass
        except IndexError as brokenIPS: pass 

        self.instances = [self.instance(self, offset = offset, data = changes[offset]) for offset in changes]
        self.bitsize = bitsize
       

    def get_instance(self, specifier : str | int | instance) -> object | None: 
        hold = self.get_instances(specifier)
        if len(hold): return hold[0]
    def get_instances(self,specifier : str | int) -> tuple:
        """
        return generator by name or ID
        :param specifier: The name or ID of desired instance
        :type specifier: str or int to match desired instance
        :return: generator to provide all potentially desired instances
        :rtype: object
        """
        return tuple(match for match in self.instances if (match.name == specifier if isinstance(specifier,str) else match.offset == specifier))
    def in_range(self,start : int = 0, end : int = None) -> tuple:
        if end is None: end = (2**self.bitsize)-1
        elif not isinstance(end, int): raise TypeError("End of range must be integral or None") 
        if not isinstance(start, int): raise TypeError("start of range must be integral or None")  
        if start < 0: raise ScopeError("Starting range cannot be negative!") 
        if end < 0: raise ScopeError("Ending range cannot be negative!")
        """
        returns generator providing instances within a range in offset
        :param int start: Starting offset for search
        :param int end: Ending offset for search
        :return: returns generator object for requested data
        :rtype: object:
        :raises TypeError: if start is not integral
        :raises TypeError: if end is not integral
        """
        return tuple(instance for instance in self.instances if instance.offset >= start and instance.offset < end) 
    def create(self, offset : int, data : tuple | bytes | bytearray, name : str = None, override : bool = False, sustain : bool = True):
        self.instances.append(self.instance(offset, data, name))
        try:
            self.instances[-1].modify(offset, data, name,override, sustain) 
            #code to insert at new offset
        except: 
            self.instances[-1].destroy()
            try: self.instances.pop(-1) 
            except IndexError: pass

        #temporary data must be IMMEDIATLY ascribed to instance, position is arbitrary as it is immediatly

        #self is ips, new is instance obj. Override is flag to avoid overwrites. #sustain attempts to keep old patch data instead of removing it.
        """
        Insert an instance into an ips object.
        :param instance new: instance needed to be implemented
        :param bool override: Override flag, should clashing data be removed. Disabled by default
        :param bool sustain: Sustain flag, should data around new data be kept by moving the patches? Enabled by default [Only triggered when overriding]
        """
        
        pass #Implement later 
    def remove(self, instances : instance | str | int) -> instance | tuple:
        """
        Used to remove an instance from an ips class
        :param patch:
        :type patch: instance or str or int
        :raises TypeError: if nor str, int or instance is provided
        :raises KeyError: if patch is not present in ips
        """
        if isinstance(instances,(str,int)):
            for ins in tuple(self.get_instances(instances)): self.remove(ins)
        elif isinstance(instances,self.instance): self.instances.remove(instances)
        else: raise TypeError("given patch is not an instance.")
        return instances   
    
    
        

def build(base : bytes | bytearray, prepatch : bytes | bytearray, legal : bool = None, bitsize : int = 24) -> bytes:
        """
        Used to create an IPS file when comparing a modified file to a base file. 
        :param base: The base file that the recepitent of the the IPS will have
        :param prepatch: The modified file that the IPS will create.
        :param bool legal: The integrity of the IPS 
        :type base: bytes or bytearray
        :type prepatch: bytes or bytearray
        :return: IPS file bytearray
        :rtype: bytearray
        :raises TypeError: if base or prepatch are not bytes or bytearray
        :raises TypeError: if legal is not bool
        :raises ScopeError: if modified file is unsuitabel for IPS generation
        :raises ScopeError: if IPS file bytes or bytearray contains illegal data.
        """

        #legal may be None, in which it will prioritize legality but will contain illegal data should it be needed to generate the file
        #bitsize will be used to dictate if the build is possible (if the file writes beyond said bitsize then whatever it is inteded for is halted)

        if not isinstance(prepatch,(bytes,bytearray)): raise TypeError("Modified file must be bytes or bytearray") #no solution
        if not isinstance(base,(bytes,bytearray)): raise TypeError("Original file must be bytes or bytearray") #no solution
        if not (isinstance(legal,bool) or legal is None): raise TypeError("`Legal` parameter must be Type `bool`")         #no solution
        if isinstance(bitsize,int):
            if bitsize % 8 or not bitsize: raise ScopeError("specified bitsize impossible")
        else: raise TypeError("`bitsize` parameter must be Type `int` or `str`")         #no solution

        fileupperlimit= 16842750 if bitsize >= 32 else (2**bitsize)-1


        if len(prepatch) > fileupperlimit:
            raise ScopeError("Modified file has data beyond target!")   #solution would be to split and append data
        elif len(prepatch) < len(base):
            raise ScopeError("Modified file is smaller than Original!") #solution would be to trim original to size of modded.
        else:
            count = 0;build=b""        
            while count != len(prepatch):
                if count == len(prepatch)-1:
                    build += count.to_bytes(3,"big")+b"\x00\x01"+bytes([prepatch[count]])
                    count += 1
                elif prepatch[count] == base[count] if count < len(base) else prepatch[count] == 0:
                    count += 1
                elif prepatch[count:count + 9] == bytes([prepatch[count]])*9:
                    for readahead in range(min(0xFFFF,len(prepatch)-count)):
                        if prepatch[count+readahead] == base[count+readahead] if count + readahead < len(base) else prepatch[count+readahead] == 0:
                            break 
                        elif prepatch[count:count+readahead] != bytes([prepatch[count]])*readahead:
                            break
                        else:
                            length = readahead+1
                    if length > 8: 
                        build += count.to_bytes(3,"big")+b"\x00\x00"+(length-1).to_bytes(2,"big")+bytes([prepatch[count]])
                        count += length-1
                    else:
                        build += count.to_bytes(3,"big")+length.to_bytes(2,"big")+prepatch[count:count+length]
                        count += length
                else:
                    for readahead in range(min(0xFFFF,len(prepatch)-count)):
                        if prepatch[count+readahead] == base[count+readahead] if count + readahead < len(base) else prepatch[count+readahead:count+readahead+5] == b"\x00"*5:
                            break 
                        else:
                            length = readahead+1 
                    build += count.to_bytes(3,"big")+length.to_bytes(2,"big")+prepatch[count:count+length]
                    count += length
            return b"PATCH"+build+b"EOF" #return bytearray of IPS file

def apply(patch : ips, base : bytes | bytearray) -> bytes:
        """
        Used to apply an IPS file when applying a patch file to a base file. 
        :param base: The base file that the recepitent of the the IPS will have
        :param patch: The IPS file that will create the intended modified result.
        :type base: bytes or bytearray
        :type ips: ips
        :return: modified bytearray
        :rtype: bytearray
        :raises TypeError: if base is not bytes or bytearray
        :raises TypeError: if ips is not of type ips
        """
        try:
            if not isinstance(patch, ips):
                raise TypeError("IPS given is not of type ips!")
            if not isinstance(base,(bytes,bytearray)):
                raise TypeError("base given is not of type bytes or bytearray!")

            build = b""
            for instance in patch.instances:      
                #if len(base) > instance.offset                         #If still overwriting
                #   build+= base[len(build):instance.offset]            #store original data up to this current point
                #else:                                                  #otherwise we are appending new bytes
                #   build+= b"\x00" * (instance.offset - len(build))    #and therefore will append zerodata until the first offset
                #if instance.rle:                                       #if instance is of type rle
                #   build+= instance.data[1]*instance.data[0]           #append bytes of hunk byte with hunk length | byte : length
                build+= (b"\x00" * (instance.offset - len(build)) if len(base) < instance.offset else base[len(build):instance.offset])+(instance.data[1]*instance.data[0] if instance.rle else instance.data)
            return build+ base[len(build):]
        except:
            raise Exception("ips class contains impossible data")
 


  #Code is still faulty
  #True overwrite will require upperlimit to be modified to recurse until final patch can be assured to exist oustide of jurisdicution of overriding patch
