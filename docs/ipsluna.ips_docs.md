# IPSLuna
`ipsluna` is the best `ips` file handler out there, while slower than it's `cpp` counterparts. `ipsluna` can boast that it offers 

- Total control of every byte in the IPS
- Serializable objects for sharing/extended use
- Produces the *smallest* `ips` files of any `ips` handler
- Lightweight filesize sitting only at `17kb`  
- extendable scope to `0x100FFFE`, or standard `0xFFFFFF`

## IPS Handling
`ipsluna` is useful for *all* elements of `ips` handling, even some that are likely to be left unused.

```python
from ipsluna.ips import *	#import ips library

with open("EXTRA MARIO BROS.ips","rb") as f:
	mod = f.read()

mod = ips(mod, False)		#construct `ips` object from file
```
We pass the `bytearray` into the constructor, and can specify whether or not this `ips` should comply to `24 bit` standards. Set to `True` by default the `optional` positional `arg` `legacy` indicates whether or no the `ips` should be allowed to write up to `0x100FFFE` which is the `32bit` limit of `ips`. Since an `ips` is just a series of `instances`, the methods within the `ips` class are just for `instance` handling:
```python
#retrieve multiple offsets within a range

header = mod.range(end=16)		#here we retrieve all instances up to the 16th byte
PRG = mod.range(16,0x8010)		#here we retrieve all instances from 16 to 0x8010
CHR = mod.range(0x8010)			#here we retrieve all instances from 0x8010 to the end

#retrieve an instance from offset, or many with a shared or unique name
mod.get(1622)					#retrieve instance starting at offset 1622
mod.get("unnamed instance at 1984 - 2010 | 26")
```

The default name on an `instance` is `unnamed instance at` to signify that it was assigned a name during construction or modification, then we get the `offset` to the `end` describing it's range including it's `size` at the end. The names do not affect how an`instance` works, it merely aids readability of the file.

An `instance`may also be created and removed from an `ips`:
```python
#This code will insert the bytearray b"Example" at 1234
mod.create(offset = 1234, data = b"Example")

#or with rle...
mod.create(offset = 1234, data = (10, b"E"))
```
If the space you are attempting to write data is occupied by another `instance` you can use the optional `kwarg` `overwrite` which will overwrite existing `instances` to make space for the new `instance`
```python
mod.create(offset = 1234, data = b"Example", override = True)
```
In the above example we keep as much of the non-clashing `instance` data within the clashing `instance`. This is due to the optional `kwarg` `sustain` default value being `True`. If the data *should not* be sustained, then this can be executed like so:
```python
mod.create(offset = 1234, data = b"Example", override = True, sustain = False)
```
However, in most cases `sustain` will likely be used, furthermore it may also be the case that the overwriting data may exist to modify existing instance data in which case it may make sense to use the optional `kwarg` `merge` which connects the new `instance` with any possible consecutive `instance`. By default `merge` is set to `False` and is only usable when `sustain` is `True`.
```python
mod.create(offset = 1234, data = b"Example", override = True, merge= True)
```
If an `instance` needs to be removed, we have the `remove` function. This function does more than just remove an `instance` however, it returns a `dict` of every `attribute` in the `instance`. Further, if the `discriminator` is a string and we have multiple `instances` it will remove them all and return a `tuple` storing all `instances` in ascending order by `offset`.
```python
dict_of_data = mod.remove(1234)											#removing by offset
tuple_of_datasets = mod.remove("unnamed instance at 1984 - 2010 | 26")	#removing by name
```
Other ways to access the `instances` in an `ips` may be index specification or slices, or using the `__iter__` method with `for`:
```python
ins = mod.instances[20]
ins = mod.instances[20:30]

ins = [ins for ins in mod if ins.size > 100]
for i in mod:
	if i.size > 100: 
		ins = i ; break
```
Once the necessary jobs regarding the `ips` is complete, you can then create a bytearray for it to be wrote to a file with `ips.to_bytes()`.

## Instance Handling
The "Total" control of `ipsluna.ips` is as advertised, the `instance` class has one method excluding initialization, which is `modify` which acts just like `ips.create` but `offset` and `data` are now optional as they have been predefined at least once.
```python
reference = mod.get(1234)
reference.modify(data = (30, b"f"), overwrite = True)
reference.modify(offset = 200, name = "New Name")
```
## Exceptions

- `ScopeError`
This `Exception` will raise when the task is infeasible given the limitations of `ips` as a system.
- `OffsetError`	
This `Exception` will raise when the task demands an impossible offset during creation or modification.

## Methods

The `apply` method takes an `ips` object and a `bytes` object for the base file.
```python
with open("Super Mario Bros. (World).nes", "rb") as f:
	base = f.read()
with open("EXTRA MARIO BROS.ips","rb") as f:
	mod = ips(f.read())
with open("EXTRA MARIO BROS.nes","wb") as f:
	f.write(apply(mod, base))
```
The `build` method takes two `bytes` objects, one for the base file and one for the target file. It also takes an optional positional `arg` `legacy` which indicates if we should allow writes up to `0x100FFFE`.
```python
with open("Super Mario Bros.nes", "rb") as f:
	base = f.read()
with open("My Cool Mario ROMhack.nes","rb") as f:
	target = f.read()
with open("My Cool Mario ROMhack.ips","wb") as f:
	f.write(build(base, target))
```
