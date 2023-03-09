# IPSLuna
`ipsluna` is not your *just* your *typical* `ips` in, `modified` out Python module. It offers total control over the skeleton of the `ips` file in ways unseen by any other `ips` tool to date.
```python
from ipsluna.ips import *
#it may be recommended for bigger projects to use...
import ipsluna.ips as ips
#or simply, if you do not need to use all the tools

#for only building
from ispluna.ips import ips,instance,i2b,build

#for only applying
from ipsluna.ips import ips,instance,b2i,apply
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
>>> (0xABCDE,(0xEF,4))#For RLE instances
```
RLE instances store the run length at position `1` in the `tuple` and the `byte` at position `0`.
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
example = patch.instances[0]#obtain first patch instance
print(example.offset)		#Find where in memory we are modifying in this patch instance
>>> 16400
print(example.rle)			#Is this an rle byte?
>>> True 					#Yes it is!
print(example.data)			#what is the data?
>>> (b"\x42",4)				#It is 0x42 four times!
example.give((b"\x32",9))	#This replaces the example instance contents with the Nine length 0x32 RLE Bytes
example.give(b"\x23\x54\x25")#This may also take noRLE

#Example also has give_RLE and give_noRLE was faster writes

example.noRLE()						#removes the RLE in order to speed up patching process (not data efficient)
example.give_name("example patch")	#This gives a patch a name, allowing for easier legitbility when being viewed later.
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
example = tuple(patch.get_instances("example patch"))[0]
#This allows us to retrieve an instance by name
example = tuple(patch.get_instances(16400))[0]
#It also works by offset!

#returns generator, so once generated data, isolate the instance in the iterable

graphic = tuple(patch.in_range(16400,40016))
#this retrieves all instances within that offset range!

graphic = tuple(patch.in_range(end=40016))
#this retrieves from 0 to 40016

graphic = tuple(patch.in_range(16400))
#this retrieves from 16400 to the end!

graphic = patch.in_range():
#this returns generator object too, working similarly to get_instances
```
Patches may also be removed:
```python
patch.remove("example patch")
#This simply removes all matching instannces from the patch in memory.
```
Finally, onto the bits that most most people care about we have building and applying.

`apply` takes two parameters `patch` and `base`:
```python
with open("modified file.bin","wb") as f:
	f.write(apply(patch,original))
``` 

The `build` function takes two parameters, and an optional `legal`, which when set prioritizes integrity over optimization.
```python
with open("patch.ips","wb") as f:
	f.write(build(original,modded))
```
`legal` does not indicate anything regarding the law, rather it serves to avoid storing original data within the patch file.
This is very important when handling sensitive data that is not in the Public Domain.

When `legal` is not set, the patch's integrity is at risk however there is the chance for a smaller and more efficient file, however should only be unset when handling Public Domain data.

## Errors:
Often a `TypeError` will be raised when invalid datatypes are passed passed into any `function` or `method` in the module.

You may receive `ScopeError` when attempting to create an instance  with an offset beyond `0xFFFFFF` or below zero.

You may also receive `ScopeError` when attempting to store data beyond the size of `0xFFFF` or with a run length longer than `0xFF`.

`OffsetError` will occur when any insertion in an ips class clashes with a pre-existing `offset`, if `override` is enabled the ips will be modified to suit the new `instance` unless `sustain` is unset, in any `instance` within range of the new `instance` will be removed.

## Traditional Usage
Many may not use the advanced features of `ipsluna` so I shall demonstrate some common usages of this module.
```python
from ipsluna import *
def build(basepath,moddedpath):
	with open(basepath,"rb") as f:
		base = f.read()
	with open(moddedpath,"rb") as f:
		mod = f.read()
	with open("patch.ips","wb") as f:
		f.write(build(mod,base))
		
def apply(basepath,patchpath):
	with open(basepath,"rb") as f:
		base = f.read()
	with open(patchpath,"rb") as f:
		mod = ips(normalize(f.read()))
	with open("modded. bin","wb") as f:
		f.write(apply(mod,base))
def hexdisplay(modfile):
	with open(modfile,"rb") as f:
		mod = ips(normalize(f.read())
	for instance in mod.instances:
		print(f"at {instance.offset} : {instance.data}"
```
But for those using the advanced features we have:
```python
from pickle import dump,load

with open("patch.ipsluna",  "wb") as f:  
	dump(ips, f)
	#for dumping python ips class

with open("patch.ipsluna","rb") as f:
	load(ips, f)
```
## Notices
A removed `instance` is not lost, the `object` still exists, and the `remove` method itself will return the data it removed.

```python
temp = []	#store removed instances
temp.append(patch.remove(instance))
#removes files and transfers to `temp`
```
Searching for `instance` in `ips` by `offest` **should** always respond with a `generator` providing an `iterable` with a length no longer than **one**, else your `ips` is broken and may respond badly.

Each `instance` is given a name like 
```python
"Unnamed instance at : 12400"
```
And therefore should not match any other instance, unless the name has been specified by inserting a new `instance` or the `give_name` method. In which case an `iterable` with a length higher than one *may occur*, for this you should always do something on the lines of this: 
```python
example = tuple(patch.get_instances("example"))[0]
#or...
example = tuple(patch.get_instances("example"))[-1]
```
Of course depending on what class you decided to make the `generator` into you may also do this:
```python
example = patch.get_instances("example")
example = tuple(patch.offset for patch in example if patch.offset%0)
```
To return all patches at that name if the offset addresses an even byte.

*This project is still in beta and the following features remain unimplemented:*
```
instance insertion
instance moving
native integrity checks
illegal ips construction
```
These features were  postponed due to their complex and rare nature and will be implemented in subsequent releases of `ipsluna`.

