## **Brette's Consumable BPS Filetype Docs**

### What is BPS?

`bps` was designed by Emulator enthusiast [byuu](https://www.romhacking.net/forum/index.php?topic=32951.0) who, with this solution, created the standard for patch files in the ROMhacking community. While in truth a successor to [`ups`](), `bps` offers a level of sophisticated versatility that was not needed when `ips` was suitable for known ROMhacking scopes.

`bps` is designed for mainly three reasons, the first being that `ips` had a soft upperlimit of about `16 MB` and therefore larger games would be unmodifiable if it were not for a successor. Secondly, `bps` does not *need* to store any `source` data beyond original file offset as it refers to `source` during patching. Finally, `bps` offers more efficient patching with incredibly low filesizes.

**Popular BPS tools include:**

 - [beat](https://www.romhacking.net/utilities/893/)
 - [Multipatch](https://www.romhacking.net/utilities/746/)
 - Tool 3

byuu developed [beat](https://www.romhacking.net/utilities/893/) alongside their `bps` filetype intended to be used in a 32bit Windows environment. [Multipatch](https://www.romhacking.net/utilities/746/) was designed for MacOSX and supports many patch filetypes including `bps`. `bps` does not have a long history like `ips` and much less tools has been developed as of writing this in 2023.


[ROM Patcher JS](https://www.marcrobledo.com/RomPatcher.js/), however eradicates the usage of executable "diff" appliers/makers as the tool is made entirely in JavaScript and therefore can use mod files and base files in a browser. (The Exception being `xdelta` files that use `Xdelta3` format which requires an x64/ARM environment that most web services cannot offer)

## How does it work?

In order to understand `bps` adequatly we need to understand the concept of `variable-width encoding` and how it works with `bps`. `variable-width encoding` is where a value (in our case numerical) is stored split into `7 bit` segments in which the MSB of said byte is an indicator to stop reading data. The result of reading through bytes until the MSB is set is our `decoded` value.

### `variable-width encoding`
```python
def encode(number : int, signed : bool = False) -> bytes:
    """
	Convert number into variable-width encoded bytes
    """

    if not isinstance(number,int): raise TypeError("Number data must be integer")
    if not isinstance(signed,bool): raise TypeError("sign flag must be boolean")
    if not signed: signed = number < 0  #set sign flag if needed
    if signed: number = abs(number * 2) + (number < 0)
	
    var_length = bytes()							#Create empty bytes object to store variable-width encoded bytes
    while True:									#Until we are finished
        x = number & 0x7f						#Using the 7 LSB of the number
        number >>= 7							#And removing such data
        if number: 								#If there is still source data to read
            var_length += x.to_bytes(1, "big")	#Append such data to our bytes object
            number -= 1							#Decrement by one to remove ambiguity
        else: 
            var_length += (0x80 | x).to_bytes(1, "big")	#Set termination byte
            return var_length 	#return result
```
### `variable-width decoding`
```python
def decode(encoded : bytes, signed : bool = False) -> int:
    """
	Decode variable-width encoded bytes into unsinged integer
    """
    if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")

    number,shift = 0, 1
    for byte in encoded:					    #for each byte in our given data
        number += (byte & 0x7f) * shift		    #increase number by data bits
        if byte & 0x80: return (number>>1)*(-1 if number & 1 else 1) if signed else number				    #return if termination bytes set
        shift <<= 7
        number += shift
```

These functions are superior in general functionality to streamlines `bytesIO` operations granted that we can interact with uncontexutal information and do not need a file to process such operations. In the solution above the data is all numerical and therefore we can rationally understand that if passed more than `16 bytes` to `decode` we would get an unfeasibly large number which Python likely would handle internally.

Since we never base our operations of the length of `bytes` with `variable-width encoding` we must (for good logic) pass a sliced value to be decoded, `bps` has a soft upperlimit of `12 exabytes` so we can use that with:
```python
decoded = decode(patch[:16])
#if the value is signed then we need do the below
decoded = (decoded >> 1)*(-1 if decoded & 1 else 1)
```
It is then only logical to then modify `patch` such that the next time we need to decode `variable-width` encoded data we do not access the same data as last time. Naturally we cannot assume the index at which we found the terminating byte in `decode`. While we *could* modify `decode` to include such a feature it would degrade on the functional convenience of the code. Therefore we can simply construct a simple subroutine for our specific task like this:
```python
encoded = b"\x45\x76\x34\x82\x43\x32\x11\xCE"
def trim(): patch = patch[patch.index([byte for byte in encoded if byte & 0x80][0]):]
decoded = decode(encoded);trim()
```

### **Header and Footer extraction**

Now that we understand this we can begin to interpret the header. The header contains a filetype indicator reading `BPS1` and three `variable-width encoded` filesizes for `source_size`, `target_size` and `metadata_size` which when larger than zero prompts to access the following `metadata` which of size recently determined.

For simplicity we can interpret the footer now, it stores three `CRC32` checksums being `source_checksum`, `target_checksum` and `patch_checksum` which are all self-explanatory. These of course are not compulsory nor are they perfect for confirming the intended arguements or result.

Unlike `ips`, `bps` does not simply write patch data from the offset to the target - but rather the instructions on how to create the result data from repositioned source, written and current target data. We call these `actions` There are four of these which vary in functionality which all are called from one main function used to determine the required operation.

```python
"""
predetermined:
    source  |   Original file
    patch   |   patch file (bps)
    target  |   resultant bytearray
    length  |   length of operation 
    relativeOffset  |   Offset used for LZ Compression
    outputOffset    |   Offset used for writing to target
"""
while len(patch): 
    #code to interpret what function to call on
    operation = decode(patch[:16]);patch = trim()                       #The entirety of the operation data
    (source_read,target_read,source_copy,target_copy)[operation & 3]()  #Function determined by indexing with 2 LSB of Operation
    
```

### **Example of a SourceRead action:**

`4c 2b 01 80`

Doesn't look like much does it? Well, first we need to `decode` the data. We then get `2135628` of which the 2LSB represent the action, which in the case of `sourceRead` is 0. Finall we shift the data two bits to the right and increment by one to retrieve the `length` of the operation.

The length is whatever is stored left in the data, in this case it is `533908`.

```python
def source_read() -> None:
    nonlocal length,source,target,outputOffset      #Code to retrieve predetermined arguements
    target[outputOffset:outputOffset+length] = source[outputOffset:outputOffset+length]     
    #Copy data form source to target
```

### **Example of a TargetRead action:**

`We need better example here` 

[redo this entirely]

```python
def target_read() -> None:
    nonlocal length, patch, target, outputOffset                #Code to retrieve predetermined arguements
    target[outputOffset:outputOffset+length] = patch[:length]   #Write in `target` bytearray a range in `patch`
    patch = patch[length:]                                      #trim patch data from patch
```

### **Example of a SourceCopy action:**

`62 35 4b 83 31 7e 64 a8`

To make that easier to read, let's break it down.

`62 35 4b 83 | 31 7e 64 a8`

In the first split we have the common instruction and lenth data, but then we also must decode additional data which includes a signed value used for relative copying. This signed value has the signature stored in the LSB used to copy data from the source to the target at different offsets.

```python
def source_copy() -> None:
    #Code to retrieve predetermined arguements
    nonlocal length, source, patch, target, outputOffset                                    
    data = decode(patch[:16]);trim()                        #code to access the signed relativeOffset
    relativeOffset = (data >> 1) * (-1 if data & 1 else 1)  #processing signed data into legible form
    target[outputOffset:outputOffset+length] = source[relativeOffset:relativeOffset+length]
    #copy source from different offset into target
```

### **Example of a TargetCopy action:**

`5a 14 23 80 4e 41 70 84`

To make that easier to read, let's break it down.

`5a 14 23 80 | 4e 41 70 84`

This code works functionally the same as `source_copy` but refers to the `target`. This is used when identical instances of mod-exclusive data exists in the `target` that can be stored as one and duplicated.

```python
def target_copy() -> None:
    #Code to retrieve predetermined arguements
    nonlocal length, patch, target, outputOffset                                    
    data = decode(patch[:16]);trim()                        #code to access the signed relativeOffset
    relativeOffset = (data >> 1) * (-1 if data & 1 else 1)  #processing signed data into legible form
    target[outputOffset:outputOffset+length] = target[relativeOffset:relativeOffset+length]
    #appending accessed target data in target
```

We use `nonlocal` to access length due to how it is predetermined during `action` identification. We also `nonlocal target` as to modify pre-existing data and not interact with a new object. Finally we `nonlocal` either `source`, `patch` or both so we do not duplicate the data in memory.



### **How to read and apply one?**

Here it will be demonstrated in very simple Python, but annotated well even when the code is verbose.

```python
def apply(patch : bytes, source : bytes) -> bytes:
    target = bytes(); outputOffset = sourceRelativeOffset = targetRelativeOffset = 0
    source_checksum, target_checksum, patch_checksum = [patch[i:i+4 if i+4 else None][::-1].hex() for i in range(-12, 0, 4)];patch = patch[4:-12]
    sourceSize = decode(patch[:16]); patch = trim()
    targetSize = decode(patch[:16]); patch = trim()
    metadataSize = decode(patch[:16]); patch = trim()
    
    if metadataSize: metadata = patch[:metadataSize];patch = patch[metadataSize:]
    else: metadata = None

    while len(patch):
        operation = decode(patch[:16]);trim()
        length, operation = (operation >> 2) + 1, operation & 3
        if operation == 3:
            relativeOffset = decode(patch[:16], True);trim()
            targetRelativeOffset += relativeOffset
            target += target[targetRelativeOffset:targetRelativeOffset+length]

        elif operation == 2:
            relativeOffset = decode(patch[:16], True);trim()
            sourcetRelativeOffset += relativeOffset
            source += source[sourcetRelativeOffset:sourcetRelativeOffset+length]

        elif operation == 1:
            target += patch[:length]
            patch = patch[length:]

        else:
            target += source[outputOffset:outputOffste+length]
        outputOffset += length
        
    return target, metadata
```
The code above accepts two `bytes` objects and will return ` bytes` object which could be parsed into a `file` object.  If you only needed this data for patching then you could :
```python
def patchfile(modfile,basefile,outfile):
	def get(File):
		with open(File,"rb") as f:
			return f.read()
	with open(outfile,"wb") as f:
		f.write(apply(get(base),get(mod)))
```
However as `patchlib.bps` is a module, usage is determined by the user and therefore despite the applications beyond standard usage being nothing short of eccentric does not invalidate the intentions.

**How does `bps` building work?**

`bps` constructing is much more detailed than `bps` applying,  as we have to account for the following things:

- Rule 1
- Rule 2
- Rule 3

`*` *Explanation 1*

`**` *Explanation 2*

`***` *Explanation 3*

Now that you know the rules, we can begin to create a `bps` file.
```python
    #Likely some technical behemoth
```

[Comment on adequacy of code]
```python
def makepatch(basefile,targetfile,outfile):
	def get(File):
		with open(File,"rb") as f:
			return f.read()
	with open(outfile,"wb") as f:
		f.write(build(get(basefile),get(targetfile)))
```

### Why do we sometimes use other patching filetypes?
`ips` was the original patch filetype, however it complied to outdated hardware limitations that makes it often unsuitable for larger tasks. `bps` is not the immediate successor to `ips`, but it is the successor to `ups` also made by byuu. 

[Much research will need to be done into `ups`]


Talk about Xdelta.

### Should I use Xdelta over `bps`?
Attempt to answer question

### Should I make my own `bps` handling tool?
As of this being written up there are not too may `bps` handlers compared to the likes of `ips`. If there is some way, be it operating system or technical feature, that `bps` has been left unfulfilled it may be logical to create these tools.



### Can I contribute towards `patchlib`?
Yes! `patchlib` GitHub allows for forks to be made and anyone with some `Python` skill can be included in the Project! In fact, there are many elements of the project left **totally** untouched that you could begin working on! If you are interested feel free in contacting on the [Discord](https://discord.com/invite/3DYCru4dCV)!
### Is it not better just to make your own filetype?

This should be overall somewhat discouraged for these reasons:

- `bps` is standardized, people may not want to use your files/tools
- It is quite likely that `bps` could solve this, people *will* use that instead
- It creates some sort of proprietary sense to it, which may deter users.
- If tool sharing is too slow for demand, users may share original files

If people do not want to use your tools then the project's popularity will be stunted, if people construct a `bps` between the base and result file then nobody will feel obliged to use *your format or tool*. In the world of common base files it is natural to assume a universal format for manipulation, for this we opt for universal filetypes, limiting control only works for immediate distribution.