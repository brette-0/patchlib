# `patchlib.bps`
`patchlib.bps` is an in-dev `bps` handler, which is currently undergoing fundamental development and has no functioning guarantee yet.

- Serialisable objects for sharing/extended us
- Checksum validation bypass *(not recommended)*

## BPS Handling
`patchlib` is useful for *most* elements of `bps` handling, even some that are likely to be left unused.

```python
from patchlib.bps import *	#import bps library

with open("Call of Cthulu.bps","rb") as f:
	mod = f.read()

mod = bps(mod, True, False)	#construct `bps` object from file
```
We pass the file contents into the constructor, and can specify whether or not this `bps` should: perform checksum validation or include optional metadata. The methods within the `bps` class are just for `instance` handling:
```python
#retrieve multiple offsets within a range

header = mod.range(end=16)		#here we retrieve all actions up to the 16th byte
PRG = mod.range(16,0x8010)		#here we retrieve all actions from 16 to 0x8010
CHR = mod.range(0x8010)			#here we retrieve all actions from 0x8010 to the end

#retrieve an instance from offset, or many with a shared or unique name
mod.get(1622)					#retrieve instance starting at offset 1622
mod.get("unnamed action at 1984 - 2010 | 26")
```

The default name on an `action` is `unnamed action at` to signify that it was assigned a name during construction or modification, then we get the `offset` to the `end` describing it's range including it's `size` at the end. The names do not affect how an`action` works, it merely aids readability of the file.

An `action` may also be created and removed from a `bps`:
```python
#This code will insert the bytearray b"Example" at 1234
mod.create(operation = 2, offset = 1234, length = 40, relative = -200)

#or with raw action...
MyAction = MyBPS[2]
mod.create(full_action = MyAction)
```

If an `instance` needs to be removed, we have the `remove` function. This function does more than just remove an `action` however, it returns a `dict` of every `attribute` in the `action`. Further, if the `discriminator` is a string and we have multiple `actions` it will remove them all and return a `tuple` storing all `actions` in ascending order by `offset`.
```python
dict_of_data = mod.remove(1234)
tuple_of_datasets = mod.remove("unnamed action at 1984 - 2010 | 26")
```
Other ways to access the `actions` in a `bps` may be index specification or slices, or using the `__iter__` method with `for`:
```python
acts = mod.actions[20]
acts = mod.actions[20:30]

acts = [acts for acts in mod if acts.length > 100]
for a in mod
	if a.size > 100: 
		act = i ; break
```
Once the necessary jobs regarding the `bps` is complete, you can then create an array of bytes for it to be wrote to a file with `bps.to_bytes()`.

## Exceptions

- `ChecksumMismatch`
This `Exception` will raise when the checksum validation fails.
- `ContinuityError`	
This `Exception` will raise when the task demands an action that would break the continuity of `bps`.

## Methods

The `apply` method takes an `bps` object and a `bytes` object for the base file.
```python
with open("Super Mario World (USA).sfc", "rb") as f:
	base = f.read()
with open("Call of Cthulu.bps","rb") as f:
	mod = bps(f.read())
with open("Call of Cthulu.sfc","wb") as f:
	f.write(apply(mod, base))
```