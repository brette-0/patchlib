# `patchlib.bps`

[Overview]

Target:

- Total control of every byte in the BPS
- Serializable objects for sharing/extended use
- Produces the *smallest* `bps` files of any `bps` handler
- Lightweight filesize
- Unsigned 128 bit integer support

## BPS Handling
`patchlib` is useful for *all* elements of `bps` handling, even some that are likely to be left unused.

```python
from patchlib.bps import *	#import bps library

with open("Curse of Cthulu.bps","rb") as f:
	mod = f.read()

mod = bps(mod)				#construct `ips` object from file
```
We pass the `bytearray` into the constructor, and can specify whether or not this `bps` object should include metadata or undergo validity checks. Set to `True` by default the `optional` positional `arg` `checks` executs some length and checksum comparisons. Since a `bps` is just a series of `operations`, the methods within the `bps` class are just for `operation` handling:
```python
#unplanned retrieval code
```

[Discuss name generation]

An `operation` may also be created and removed from an `ips`:
```python
#unplanned creation code
```
[Discuss means of overwriting (needed with bps)]
```python
#more configurable code?
```
[removal]
```python
#unplanned removal code
```
Other ways to access the `operations` in a `bps` may be index specification or slices, or using the `__iter__` method with `for`:
```python
oper = mod.operations[20]
oper = mod.operations[20:30]

ins = [ins for ins in mod if ins.size > 100]
for oper in mod:
	if oper.length > 100: 
		ins = oper ; break
```
Once the necessary jobs regarding the `bps` is complete, you can then create a bytearray for it to be wrote to a file with `bps.to_bytes()`.

## Instance Handling
```python
#unsure how this will go as all modificaitons will likely end up creating/removing
```
## Exceptions

- `ChecksumMismatch`
This `Exception` will raise when the current and desiresd checksum do not match. This can be bypassed by disabling checks.

## Methods

The `apply` method takes a `bps` object and a `bytes` object for the base file.
```python
with open("Super Mario World. [USA].sfc", "rb") as f:
	base = f.read()
with open("Curse of Cthulu.bps","rb") as f:
	mod = ips(f.read())
with open("Curse of Cthulu.sfc","wb") as f:
	f.write(apply(mod, base, metadata = False))
```
[Overview building]
```python
with open("Super Mario World.sfc", "rb") as f:
	base = f.read()
with open("My Cool Mario ROMhack.sfc","rb") as f:
	target = f.read()
with open("My Cool Mario ROMhack.bps","wb") as f:
	f.write(build(base, target))
```
