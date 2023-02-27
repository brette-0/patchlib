def b2i(bytelist):  #Accept bytearray
  build = ""
  for i in range(0, len(bytelist)):  #For each byte
    build += ("0" * (2 - len(hex(bytelist[i])[2:]))) + hex(bytelist[i])[2:]
  return int(build, base=16)


def i2b(number : int,bytesize : int): #convert integral number to xbytes
    build = []
    for depth in range(bytesize-1,-1,-1):
        build.append(number//(256**depth))
        number -= (number//(256**depth))*(256**depth)
    return bytes(build)

def normalize(patch : bytes):
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
    def __init__(self,offset : int,data : bytes | bytearray | tuple,name : str = None):
        self.rle,self.offset,self.data = type(data) == tuple,offset,data 
        self.size = data[1] if self.rle else len(data)
        self.name = name if name != None else f"Unnamed patch at {offset}"
    def give_name(self,name : str):
        self.name = name
    def noRLE(self):
        if self.rle:
            self.rle = False
            self.data = tuple(self.data[0]*self.data[1])
    def give_RLE(self,byte,length):
        if type(byte) != bytes | bytearray:
            raise Exception(f"Type Error : {byte} is not bytes or bytearray object.")
        if type(length) != int:
            raise Exception(f"Type Error : {length} is not integer")
        if length > 256 or length < 0:
            raise Exception(f"RLE Error : {length} is either above 255 and therefore too large, or smaller than zero and therefore impossible!")
        if len(byte) != 1:
            raise Exception(f"RLE ERROR : {byte} is either too long or zero length, please ensure that this is a singular byte!")
        if length == 0:
            print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
        self.rle = True 
        self.data = tuple(byte,length)
    def give_noRLE(self,data):
        if type(data) != bytes | bytearray:
            raise Exception(f"Type Error : {data} is not bytes or bytearray type!")
        if len(data) > 255 or len(data) < 0:
            raise Exception(f"Number Error : {data} is either above 255 and therefore too large, or smaller than zero and therefore impossible!")
        if len(data) == 0:
            print("Warning : Zero Length data has been wrote, this will not write anything and may break some IPS patchers.")
        self.rle = False
        self.data = data
    def give(self, data : tuple | bytes | bytearray): 
        if type(data) == tuple:
            self.give_RLE(data) 
        if type(data) == bytes | bytearray: 
            self.give_noRLE(data)

            #lack of specifism amounts to innacuracy, ensure RLE where requried.
        pass
    
        
        

class ips():
    def __init__(self, normalized : dict):
        self.instances = []
        for offset in normalized.keys():
            self.instances.append(instance(offset=offset,data=normalized[offset]))
    def get_instance(self,specifier : str | int):
        match = [match for match in self.instances if (match.name == specifier if type(specifier) == str else match.offset == specifier)] 
        return match[0] if len(match) > 0 else None
    def in_range(self,start : int, end : int = None):
        return [instance for instance in self.instances if instance.offset > start and (instance.offset < end if type(end) == int else True)]
    def insert(self, new : instance, override : bool = False, sustain : bool = True):
        #self is ips, new is instance obj. Override is flag to avoid overwrites. #sustain attempts to keep old patch data instead of removing it.
        if type(new) != instance:
            raise Exception(f"Type Error : {new} is not of type `instance`")
        
        if True in [match.offset == new.offset for match in self.instances] and not override:
            raise Exception(f"Offset Error : {new.offset} is occupied.")

        lowercheck = self.in_range(0,new.offset)    #find lower neighbor
        if len(lowercheck) > 0:
            lowercheck = lowercheck[-1]
        else:
            lowercheck = instance(0,(b"\x00",0),"Lower Check")

        if lowercheck.offset + lowercheck.size > new.offset:    #if last patch is in range of new patch
            if override and lowercheck.name != "Lower Check":
                if sustain:
                    temp = instance(lowercheck.offset,lowercheck.data,lowercheck.name) 
                    if temp.rle:
                        temp.give_RLE(temp.data[0],(lowercheck.offset + lowercheck.size)-new.offset)
                    else:
                        temp.give_noRLE(temp.data*((lowercheck.offset + lowercheck.size)-new.offset))
                    self.remove(lowercheck)
                    self.insert(temp)   #insert new trimmed patch at current pos, raise warning if need be
                else:
                    self.remove(lowercheck)                 #remove patch if no sustain and taking place with override enabled
            else:
                raise Exception(f"Offset Error : {lowercheck.name} writes to areas in {new.name}") 
        uppercheck = self.in_range(new.offset)  #read from new.offset to end
        if len(uppercheck) > 0:
            uppercheck = uppercheck[0]
        else:
            uppercheck = instance(0xFFFFFF,(b"\x00",0),"Upper Check")   #Zero data at final offset
        if new.offset + new.size > uppercheck.offset:
            if override and uppercheck.name != "Upper check":
                if sustain:
                    temp = instance(new.offset+new.size,uppercheck.data,uppercheck.name) 
                    if temp.rle: 
                        temp.give_RLE(temp.data[0],(new.offset+new.size)-uppercheck.offset) 
                    else:
                        temp.give_noRLE(temp.data*((new.offset+new.size)-uppercheck.offset)) 
                    self.remove(uppercheck) 
                    self.insert(temp) 
                else:
                    self.remove(uppercheck)
            else:
                raise Exception(f"Offset Error : {uppercheck.name} writes to areas in {new.name}") 
        self.instances.insert(self.instances.index(uppercheck) if uppercheck.name != "Upper check" else -1,new)



    def remove(self, patch : instance | str | int):
        if type(patch) == str | int:
            patch = self.get_instance(patch)
        if type(patch) != instance:
            raise Exception(f"Type Error : {patch} is not an instance.")
        else:
            self.instances.remove(patch)    #Python will raise error by missing value
    def move(self, Instance : instance, offset : int,override):
        if type(patch) == str | int:
            patch = self.get_instance(patch)
        if type(Instance) != instance:
            raise Exception(f"Type Error : {Instance} is not an instance.")
        if Instance not in self.instances:
            raise Exception(f"Key Error : {Instance} is not an instance in this class")
        if offset > 0xFFFFFF or offset < 0:
            raise Exception(f"Number Error : {offset} is either over 16777215 or smaller than zero which is impossible!")
        hold = Instance 
        self.instances.remove(Instance)  
        self.insert(instance(offset,hold.data,hold.name),override)
        

def build(base : bytes | bytearray, prepatch : bytes,specifics : list | tuple = [],legal : bool = True):
        if not "nosizecheck" in specifics and len(prepatch) >16842750:
            return False, "Size Check Failure"
            
        count = 0        
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

def apply(patch : ips, rom : bytes,header : bytes = b""):
      build = b""
      for instance in patch.instances:      
           build+= (rom[len(build):instance.offset] if len(rom) > instance.offset else b"\x00" * (instance.offset - len(build)))+(instance.data[0]*instance.data[1] if instance.rle else instance.data)
      return header+build+ rom[len(build):]
 


  #Code is still faulty
  #True overwrite will require upperlimit to be modified to recurse until final patch can be assured to exist oustide of jurisdicution of overriding patch