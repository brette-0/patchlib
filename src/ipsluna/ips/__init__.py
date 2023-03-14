def b2i(bytelist) -> int:  #Accept bytearray
  build = ""
  for i in range(0, len(bytelist)):  #For each byte
    build += ("0" * (2 - len(hex(bytelist[i])[2:]))) + hex(bytelist[i])[2:]
  return int(build, base=16)


def i2b(number : int,bytesize : int) -> bytearray: #convert integral number to xbytes
    build = []
    for depth in range(bytesize-1,-1,-1):
        build.append(number//(256**depth))
        number -= (number//(256**depth))*(256**depth)
    return bytes(build)

class OffsetError(Exception):
    """
    Raised when attepting to perform an illegal operation due to offset clashing
    """
    pass

class ScopeError(Exception):
    """
    Raised when job scope exceeds limitations of IPS.
    """

class FileError(Exception):
    """
    Raised when IPS bytearray is illegal.
    """


def normalize(patch : bytes | bytearray) -> dict:
      """
      Normalizes raw ips bytearray | bytes file.
      :param patch: the raw contents of the patch
      :type patch: bytes or bytearray
      :return: Dictionary by offset: data, or offset: (byte, Length)
      :rtype: dict
      """
      count, changes,patch = 0, {}, patch[5:-3]
      while count != len(patch):
        count += 8
        if patch[count - 5] > 0 or patch[count - 4] > 0:
            size = b2i(patch[count - 5:count - 3])
            changes[b2i(patch[count-8:count - 5])] = patch[count - 3:count + size - 3]
            count += size - 3
        else:  #Handle RLE, only if NON-RLE is not met     
            changes[b2i(patch[count-8:count - 5])] = (bytes([patch[count - 1]]),b2i(patch[count - 3:count - 1]))       
      return changes



class instance():
    """
    Task stored in ips file storing data for modification. 
    """
    def __init__(self,offset : int,data : bytes | bytearray | tuple,name : str = None):
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
        if not isinstance(data,(bytes,bytearray,tuple)):
            raise TypeError("Instance data is invalid!")
        if len(data) != 2 if isinstance(data,tuple) else False:
            raise FileError("Tuple has invalid data!")
        if type(offset) != int:
            raise TypeError("Offset is not integral!")
        if offset > 0xFFFFFF:
            raise ScopeError("Offset exceeds limitations of IPS")
        if offset < 0:
            raise ScopeError("Offset is below zero and therefore impossible!")
        if type(name) != str and name is not None:
            raise TypeError("Given name is not of type string and is therefore unsuitable")
        self.rle,self.offset,self.data = type(data) == tuple,offset,data 
        self.size = data[1] if self.rle else len(data)
        self.end = self.offset + self.size
        self.name = name if name is not None else f"Unnamed patch at {offset}"
    def give_name(self,name : str):
        """
        Allows the user to provide the instance a specified name
        :type str name: The name to give to the instance
        :raises TypeError: if name is not string
        """
        if type(name) != str:
            raise TypeError("Given name is not of type String!")
        self.name = name if type(name) == str else self.name
    def noRLE(self):
        """
        Converts instance of RLE to noRLE
        """
        if self.rle:
            self.rle = False
            self.data = tuple(self.data[0]*self.data[1])
        self.end = self.offset + self.size
    def give_RLE(self,byte : bytes | bytearray,length : int) -> tuple:
        """
        Gives immediate RLE instance to specified instance.
        :param byte: The byte to be looped in RLE
        :param int length: The run length for the byte.
        :type byte: bytes or bytearray
        :return: tuple by (byte,offset)
        :rtype: tuple
        :raises TypeError: if byte is not of type `bytes` or `bytearray`
        :raises TypeError: if length is not integral
        :raises ScopeError: if length is over 0xFF or less than zero.
        :raises ScopeError: if length of `byte` is does not equal one.
        """
        if not isinstance(byte,(bytes,bytearray)):
            raise TypeError(f"Type Error : {byte} is not bytes or bytearray object.")
        if type(length) != int:
            raise TypeError(f"Type Error : {length} is not integer")
        if length > 256 or length < 0:
            raise ScopeError(f"RLE Error : {length} is either above 255 and therefore too large, or smaller than zero and therefore impossible!")
        if len(byte) != 1:
            raise ScopeError(f"RLE ERROR : {byte} is either too long or zero length, please ensure that this is a singular byte!")
        if length == 0:
            print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
        self.rle = True 
        self.data = (byte,length)
        self.end = self.offset + self.size
        return self.data
    def give_noRLE(self,data : bytes | bytearray) -> bytearray:
        """
        Gives immediate noRLE instance to specified instance.
        :param data: The byte to be looped in RLE
        :type data: bytes or bytearray
        :return: bytearray of data
        :rtype: bytearray
        :raises TypeError: if data is not of type `bytes` or `bytearray`
        :raises ScopeError: if length of data is over 0xFFFF or less than zero.
        """
        if not isinstance(data,(bytes,bytearray)):
            raise TypeError(f"Given data is not bytes or bytearray type!")
        if len(data) > 0xFFFF or len(data) < 0:
            raise ScopeError(f"Given data is either above 65535 and therefore too large, or smaller than zero and therefore impossible!")
        if len(data) == 0:
            print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
        self.rle = False
        self.data = data
    def give(self, data : tuple | bytes | bytearray) -> tuple | bytearray: 
        """
        nospecific data modifier used for human interaction or unkown instance type
        :param data: The data to insert into the instance
        :type data: bytes or bytearray or tuple
        :return: bytearray or tuple of data
        :rtype: tuple or bytearray
        :raises TypeError: if data is not of type `bytes` or `bytearray`
        :raises ScopeError: if length of data is over 0xFFFF or less than zero.
        """
        if isinstance(data,tuple): return self.give_RLE(data) 
        if not isinstance(data,(bytes,bytearray)): return self.give_noRLE(data)
        raise TypeError("Unexpected type for data!")
    
        
        

class ips():
    """
    class supporting intimate interactions with the normalized ips data.
    """
    def __init__(self, normalized : dict):
        """
        initialization maps out all instances in normalized dictionary into `instances`
        :raises TypeError: if normalized is not type `dict`
        """
        self.instances = []
        if not isinstance(normalized,dict):
            raise TypeError("normalized is not type `dict` and therefore cannot be accessed")
        for offset in normalized.keys():
            self.instances.append(instance(offset=offset,data=normalized[offset]))
    def get_instances(self,specifier : str | int) -> object:
        """
        return generator by name or ID
        :param specifier: The name or ID of desired instance
        :type specifier: str or int to match desired instance
        :return: generator to provide all potentially desired instances
        :rtype: object
        """
        return (match for match in self.instances if (match.name == specifier if type(specifier) == str else match.offset == specifier))
    def in_range(self,start : int = 0, end : int = None) -> object:
        """
        returns generator providing instances within a range in offset
        :param int start: Starting offset for search
        :param int end: Ending offset for search
        :return: returns generator object for requested data
        :rtype: object:
        :raises TypeError: if start is not integral
        :raises TypeError: if end is not integral
        """
        return (instance for instance in self.instances if instance.offset > start and (instance.offset < end if type(end) == int else True))
    
    def insert(self, new : instance, override : bool = False, sustain : bool = True):
        #self is ips, new is instance obj. Override is flag to avoid overwrites. #sustain attempts to keep old patch data instead of removing it.
        """
        Insert an instance into an ips object.
        :param instance new: instance needed to be implemented
        :param bool override: Override flag, should clashing data be removed. Disabled by default
        :param bool sustain: Sustain flag, should data around new data be kept by moving the patches? Enabled by default [Only triggered when overriding]
        """
        if not isinstance(new,instance):
            raise TypeError(f"Given instance is not of type `instance`")
        
        if True in [match.offset == new.offset for match in self.instances] and not override:
            raise OffsetError("Offset is occupied")

        if len(self.instances):
            self.instances.insert(-1, new)
        
        lowercheck = tuple(self.in_range(0,new.offset))         #get tuple of instances until offsets
        if len(lowercheck) > 0:                                 #if there is a preceeding instance
            lowercheck = lowercheck[-1]                         #retrieve the last
        else:
            lowercheck = instance(0,(b"\x00",0),"internal_ips_lowercheck")  #otherwise create object with empty data for comparison

        
        
        if lowercheck.end > new.offset:    #if last patch is in range of new patch
            if override and lowercheck.name != "internal_ips_lowercheck":   #check that this is not the bogus data (this can be ignored)
                if sustain:                                     #if attempting to maintain as much of the mod as possible
                    temp = instance(lowercheck.offset,lowercheck.data,lowercheck.name)  #Create temporary object to replace the instance at lowercheck offset
                    if temp.rle:
                        temp.give_RLE(temp.data[0],new.offset-lowercheck.offset)    #Write up to offest
                    else:
                        temp.give_noRLE(temp.data[:new.offset-lowercheck.offset])   #Write up to offset
                    self.instances.insert(self.instances.index(lowercheck),temp)
                    self.remove(lowercheck)
                else:
                    self.remove(lowercheck)                     #remove patch if no sustain and taking place with override enabled
            else:
                raise OffsetError(f"{lowercheck.name} writes to areas in {new.name}") 

        uppercheck = tuple(self.in_range(new.offset, new.offset + new.size)) 

        if not len(uppercheck):
            if sustain: temp = (instance(0xFFFFFF, (b"\x00",0), "internal_ips_uppercheck"))
            elif not override: raise OffsetError(f"Data between offsets {new.offset} and {new.offset + new.data} are already being used.")


        if uppercheck[0].name != "internal_ips_uppercheck" and override:
            for ins in uppercheck[:-1 if sustain else None]:
                self.instances.remove(ins) 
        uppercheck = uppercheck[-1] 

        if sustain and override and not uppercheck.name == "internal_ips_uppercheck":
            temp = instance(new.offset + new.size, uppercheck.data)
            if uppercheck.rle:
                temp.give_RLE(temp.data[0],uppercheck.end - temp.offset)
            else:
                temp.give_noRLE(temp.data[uppercheck.end - temp.offset:])
            self.instances.insert(self.instances.index(uppercheck),temp) 
            self.remove(uppercheck) 

        self.instances.insert(self.instances.index(temp), new)



        
        


       
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
        elif isinstance(instances,instance): self.instances.remove(instances)
        else: raise TypeError("given patch is not an instance.")
        return instances

    """
    def move(self, Instance : instance, offset : int,override : bool = False, sustain : bool = True):
        if isinstance(Instance,(str,int)):
            Instance = self.get_instance(Instance)[0]
        if not isinstance(Instance,instance):
            raise Exception(f"Type Error : {Instance} is not an instance.")
        if Instance not in self.instances:
            raise Exception(f"Key Error : {Instance} is not an instance in this class")
        if offset > 0xFFFFFF or offset < 0:
            raise Exception(f"Number Error : {offset} is either over 16777215 or smaller than zero which is impossible!")
        hold = Instance 
        self.instances.remove(Instance)  
        self.insert(instance(offset,hold.data,hold.name),override, sustain)
    """
        

def build(base : bytes | bytearray, prepatch : bytes | bytearray, legal : bool = None, bitsize : int | str = 24) -> bytearray:
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
        :raises FileError: if IPS file bytes or bytearray contains illegal data.
        """

        #legal may be None, in which it will prioritize legality but will contain illegal data should it be needed to generate the file
        #bitsize will be used to dictate if the build is possible (if the file writes beyond said bitsize then whatever it is inteded for is halted)

        if not isinstance(prepatch,(bytes,bytearray)): raise TypeError("Modified file must be bytes or bytearray") #no solution
        if not isinstance(base,(bytes,bytearray)): raise TypeError("Original file must be bytes or bytearray") #no solution
        if not (isinstance(legal,bool) or legal is None): raise TypeError("`Legal` parameter must be Type `bool`")         #no solution
        if isinstance(bitsize,str):
            if True in [l for l in bitsize if l not in list(range(10))]: raise TypeError("`bitsize` parameter must only contain positive integral values")
            bitsize = int(bitsize)
        elif not isinstance(bitsize,int): raise TypeError("`bitsize` parameter must be Type `int` or `str`")         #no solution

        fileupperlimit= 16842750 if bitsize >= 32 else (2**bitsize)-1


        if len(prepatch) > fileupperlimit:
            raise ScopeError("Modified file has data beyond target!")   #solution would be to split and append data
        elif len(prepatch) < len(base):
            raise ScopeError("Modified file is smaller than Original!") #solution would be to trim original to size of modded.
        else:
            count = 0;build=b""        
            while count != len(prepatch):
                if count == len(prepatch)-1:
                    build += i2b(count,3)+b"\x00\x01"+bytes([prepatch[count]])
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
                        build += i2b(count,3)+b"\x00\x00"+i2b(length-1,2)+bytes([prepatch[count]])
                        count += length-1
                    else:
                        build += i2b(count,3)+i2b(length,2)+prepatch[count:count+length]
                        count += length
                else:
                    for readahead in range(min(0xFFFF,len(prepatch)-count)):
                        if prepatch[count+readahead] == base[count+readahead] if count + readahead < len(base) else prepatch[count+readahead:count+readahead+5] == b"\x00"*5:
                            break 
                        else:
                            length = readahead+1 
                    build += i2b(count,3)+i2b(length,2)+prepatch[count:count+length]
                    count += length
            return b"PATCH"+build+b"EOF" #return bytearray of IPS file

def apply(patch : ips, base : bytes | bytearray) -> bytearray:
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
            if type(patch) != ips:
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
                #   build+= instance.data[0]*instance.data[1]           #append bytes of hunk byte with hunk length | byte : length
                build+= (base[len(build):instance.offset] if len(base) > instance.offset else b"\x00" * (instance.offset - len(build)))+(instance.data[0]*instance.data[1] if instance.rle else instance.data)
            return build+ base[len(build):]
        except:
            raise Exception("ips class contains impossible data")
 


  #Code is still faulty
  #True overwrite will require upperlimit to be modified to recurse until final patch can be assured to exist oustide of jurisdicution of overriding patch
