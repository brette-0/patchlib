> 

# IPSLuna
IPSLuna is not *just* your common `patch in` `patched out` module.
```python
from ipsluna import *
```
Then access the IPS patch with:
```python
with open("modfile.ips","rb") as f:
	patch = f.read()
```
Since the file is an unprocessed `bytearray`, `ipsluna` supports the function `normalize` the raw file into a `dictionary` like:
```python
patch = normalize(patch)
for instance in patch.items():
	print(instance)
>>> (0xABCD,0xFE)	  #For nonRLE instances
>>> (0xABCDE:(0xEF,4))#For RLE instances
```
RLE, or Run Length Encoding, instances store the run length at position `1` in the `tuple` and the `byte` specified at position `0`.
This data *should* be chronologically ordered as all working IPS file should be, a quick check with:
```python
def checkNormalized(keys : dict_keys):
	keys = (list(keys),len(dict_keys)-1)
	for key in range(keys(1)):
			if keys[key] > keys[key+1]
			return False
	else:
			return True
```
Or if you cannot be bothered to test a working file, simply use:
```python
try:
	#do ips functions here, error will be reported below
except error:
	print(error) #log error in shell, may not be ips fault
```
Once we can assume a normalized IPS dictionary we create a custom class for said IPS file with:
```python
patch = ips(patch)	#create instance of patch class using normalized dictionary
```
From this we can understand the patch in more detail:
```python
print(len(patch.instances))	#This will show us how many patch instances there are
>>> 321		#This tells there are 321 patch instances in this file
print(patch.instances[-1].offest + patch.instances[-1].size)
>>> 40016	#This tells us the last byte the patch wrote to
```
Other than just metadata commands, the `instance` object stores some interesting data itself.
```python
example = patch.instances[0]	#obtain first patch instance
print(example.offset)	#Find where in memory we are modifying in this patch instance
>>> 16400
print(example.rle)		#Is this an rle byte?
>>> True 				#Yes it is!
print(example.data)		#what is the data?
>>> (b"\x42",4)			#It is 0x42 four times!
print(example.verbose)	#Has this patch been made with verbose data access?
>>> False 				#This means that RLE can not be read as noRLE, this is more efficient by memory.
example.give((b"\x32",9))	#This replaces the example instance contents with the Nine length 0x32 RLE Bytes
example.give(b"\x23\x54\x25")#This may also take noRLE
#Example also has give_RLE and give_noRLE was faster writes
example.noRLE()	#removes the RLE in order to speed up patching process (not data efficient)
example.give_name("example patch") #This gives a patch a name, allowing for easier legitbility when being viewed later.
```
IPS files are build on these instances, they make up how the file functions, describing the `offset`, `size` and `data` of the `instance` contents. 

Example of `noRLE` `instance`:
`01 23 45 | 00 05 | 67 89 AB CD EF`
`_offset_` `length_` `data...........`

Example of `RLE` `instance`:
`01 23 45 | 00 00 | 67 | 89`
`_offset_` `_zeroes` `byte` `length`

The `ips` class stores all of these `instances` in the array, since `class` objects are awkward to navigate manually, there is a variety of commands within the `ips` class allowing for competent `instance` handling.
```python
example = patch.get_instance("example patch")
#This allows us to retrieve an instance by name
example = patch.get_instance(16400)
#It also works by offset!

graphic = patch.in_range(16400,40016)
#this retrieves all instances within that offset range!
```
You can also insert a new `instance` into a pre-loaded `ips`:
```
custom= instance(16416,(b"\x00",8)","clear tile 2")
patch.insert(custom)
#position is based of offset, and is inserted chronologically in ips
>>> Offset Error : clear tile 2 clashed with Unnamed patch at 16416
#In which case we can override!
patch.insert(custom,True) 
```
Patches may also be moved and removed:
```python
patch.move("example patch",01234)
#This is actually just fetching the instance, storing it, deleting it, modifying it's offset and re-inserting it!
patch.remove("example patch")
#This simply removes the patch from memory.
```
Finally, onto the bits that most most people care about we have building and applying.

`apply` takes `2` compulsory parameters and `1` optional parameter.
```python
with open("new rom.game","wb") as f:
	f.write(apply(patch,original))
``` 
IPSLuna's `header` optional parameter may be used to store information to precede the result before returning.

The `build` function takes `2` compulsory parameters and offers `2` optional parameters!
```python
with open("patch.ips","wb") as f:
	f.write(build(original,modded))
```
You may even in the third parameter of type `tuple` include the string `nosizecheck` to bypass size check security.
`appendbaseheader` will append base header, and `appendmodheader` will append mod header.

The fourth parameter `legal` of type `bool` refers to nothing of law, but simply of file integrity. This is set to `True` by default but when disabled will provide potentially smaller or faster patches but may contain the `original` data.
