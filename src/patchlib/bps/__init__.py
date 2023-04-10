"""
experimental alpha bps handler
"""

__version__ = "0.1"

def encode(data : int) -> bytearray:  #create function return bytearray, takes int
    """
    encodes standard 64bit int, may be higher, into variable width beat bytearray
    """

    #encoded is built bytearray to return
    #x is used to store byte contents
    #data, after x is extracted, will be used for loop logic
    encoded = b""                       #create bytearray for return
    while True:                         #create indefinte loop
        x = data & 0x7f                 #create temporary variable "x" with "content" of byte | taking it's lower 7LSBs
        data >>= 7                      #trim last 7 bytes off
        if data == 0:                   #if data is equivalent to zero, write signed MSB + stored 7 LSBs
            encoded+=bytes([0x80 | x])  
            break                       #exit loop
        encoded+=bytes([x])             #else if not end, loop after appending stored 7lSBs with
        data-=1                         #decrement at the end
    return encoded                      #return bytearray of encoded contents

    """
    mimic:
    Encoding

    //x is used to store byte contents
    //data, after x is extracted, will be used for loop logic

    void encode(uint64 data) {          //create function accepting "data" as unsigned 64bit integer
      while(true) {                     //create indefinite loop
        uint8 x = data & 0x7f;          //create temporary variable "x" with "content" of byte | taking it's lower 7LSBs
        data >>= 7;                     //trim last 7 bytes off
        if(data == 0) {                 //if data is equivalent to zero, write signed MSB + stored 7 LSBs
            write(0x80 | x);
            break;                      //exit loop
            }
        write(x);                       //else if not end, loop after appending stored 7LSBs with
        data--;                         //decrement at end
     }
    }
    """                                 #C++ source

def decode(data : bytes) -> int:        #create function decode for unsigned 64 bit integer (beat does allow up to 128)
    number,shift = 0,1                  #create variables "data" and "shift" all of type unsigned 64 bit integer with data : 0 and 1
    while True:                         #create indefinite loop
        x = ord(data[-1:])              #create x as 8 LSB of read
        number += (x & 0x7f) * shift    #add 7LSB of "x" multiplied by shift, to our rerturn variable "data"
        if x & 0x80: break              #if d0 of x is set exit loop for break
        shift <<= 7                     #trim 7 bytes off start of shift
        number += shift                 #add shift to data

    return number                       #return

    """
    uint64 decode() {                   //create function decode for unsigned 64 bit integer (beat does allow up to 128)
        uint64 data = 0, shift = 1;     //create variables "data" and "shift" all of type unsigned 64 bit integer with data : 0 and 1
        while(true) {                   //create indefinite loop
            uint8 x = read();           //create x as 8 LSB of read
            data += (x & 0x7f) * shift; //add 7LSB of "x" multiplied by shift, to our rerturn variable "data"
            if(x & 0x80) break;         //if d0 of x is set exit loop for break
            shift <<= 7;                //trim 7 bytes off start of shift
            data += shift;              //add shift to data
        }
     return data;                       //return
    }
    """


def normalize(bps : bytes | bytearray) -> dict: 
    normalized = {};bps = bps[4:]

    normalized ["Source Size"] = decode(bps[:16])                           #Decode Source Size   | read 16 bytes ahead for u128i
    bps = bps[bps.index([byte for byte in bps[:16] if byte & 128][0]):]     #trim bps from first d0 enabled byte
    normalized ["Target Size"] = decode(bps[:16])                           #Decode Target Size   | read 16 bytes ahead for u128i
    bps = bps[bps.index([byte for byte in bps[:16] if byte & 128][0]):]     #trim bps from first d0 enabled byte
    normalized ["Metadata Size"] = decode(bps[:16])                         #Decode Metadata Size | read 16 bytes ahead for u128i
    bps = bps[bps.index([byte for byte in bps[:16] if byte & 128][0]):]     #trim bps from first d0 enabled byte
    
    normalized["Metadata"] = bps[:normalized["Metadata Size"]]              #Gather Metadata as bytearray (should be xml | may not be)
    bps = bps[normalized["Metadata Size"]:]                                 #trim bps to exclude metadata

    normalized["source-checksum"] = bps[-24:-16]                            #Source file checksum
    normalized["target-checksum"] = bps[-16:-8]                             #Target file checksum 
    normalized["patch-checksum"] = bps[-8:]                                 #bps file checksum

    bps = bps[:-24]                                                         #trim Footer


    return normalized


class bps():
    def __init__(self, normalized : dict):
        #from dict generate instance data
        pass

class instance():
    def __init__(self, actions : int):
        """
        actions (nybble) indicates actions in instance
        """
        if actions not in range(0,16):
            raise Exception("Invalid complexity Parameter")                #Decide some exception

        if actions & 8:
            pass 
        if actions & 4:
            pass 
        if actions & 2:
            pass 
        if actions & 1:
            pass



class action():
    def __init__(self, action : str | int):
        if ["SourceRead","TargetRead","SourceCopy","TargetCopy","Exception"].index(4 if action not in range(0,4) else action) if isinstance(action,int) else action in ["SourceRead","TargetRead","SourceCopy","TargetCopy"]:
            self.action = action 
        else:
            raise Exception("Action type not specified")                   #Decide some exception
        
