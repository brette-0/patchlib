## Brette's Consumable IPS Filetype Docs

### What is IPS?

The `IPS` or `International Patching System` filetype was created in 1993 to express "diffs" between a controlled `base` file and a resultant `target` file. MS-DOS at this point was the most popular operating system and some versions could not store a `32 bit` number due to limitations of the time.

The `IPS` filetype was developed my Japanese ["ROM-Hackers"](https://en.wikipedia.org/wiki/ROM_hacking) who wished to share their modifications in a way that did not promote or commit acts of digital piracy, these files were spread on file hosting/shareware and forum websites before mainstream ROM-Hacking communities were established such as [Super Mario World Central](https://www.smwcentral.net/) which stores the largest archive of [Super Mario World](https://www.mariowiki.com/Super_Mario_World) ROM-Hacks, and is the most popular use for this filetype.

**Popular IPS tools include:**

 - [Lunar IPS](https://www.romhacking.net/utilities/240/)  
 -  [Floating IPS](https://www.romhacking.net/utilities/1040/) 
 - [EWing IPS Patcher](https://www.romhacking.net/utilities/1297/)

[Lunar IPS](https://www.romhacking.net/utilities/240/) is the most popular, but does not support `BPS` like [Floating IPS](https://www.romhacking.net/utilities/1040/)  does. All the above are designed for Windows Systems except [EWing IPS Patcher](https://www.romhacking.net/utilities/1297/) which should work on any `Posix` System. 
 
 **As well as historic ones such as:**
 
 - [IPS](https://www.romhacking.net/utilities/8/)
 - [IPSMac](https://www.romhacking.net/utilities/15/)
 - [JIPS](https://www.romhacking.net/utilities/946/)
 
[IPS](https://www.romhacking.net/utilities/8/) is designed for 90's Windows Operating Systems such as MS-DOS, [IPSMac](https://www.romhacking.net/utilities/15/) is designed for early Macintosh systems, and [JIPS](https://www.romhacking.net/utilities/946/) is simply an `ips` handler designed in Java.

 **As well as more developmental IPS tools:**
 
 - [IPS Peek](https://www.romhacking.net/utilities/1038/)
 - [`ips.py`](https://www.romhacking.net/utilities/1280/)
 - [Chief-Net IPS](https://www.romhacking.net/utilities/578/)

[IPS Peek](https://www.romhacking.net/utilities/1038/) and [Chief-Net IPS](https://www.romhacking.net/utilities/578/) both allow selective patching, meaning that parts of the IPS may be excluded or included when patching by the users choice.[`ips.py`](https://www.romhacking.net/utilities/1280/) is a Python `ips` tool, however it is not as versatile as `patchlib` which is the *recommended*  Python IPS Module.

[ROM Patcher JS](https://www.marcrobledo.com/RomPatcher.js/), however eradicates the usage of executable "diff" appliers/makers as the tool is made entirely in JavaScript and therefore can use mod files and base files in a browser. (The Exception being `xdelta` files that use `Xdelta3` format which requires an x64/ARM environment that most web services cannot offer)

### How does it work?

Simple, an IPS file has a static Header reading `PATCH` and a Footer reading `EOF`. The middle of the IPS file is a series of unterminated series of bytes. These "instances" come in two forms in variable size.

**Example of a noRLE Instance:**

`01 23 45 00 05 67 89 AB CD EF`

To make that easier to read, let's break it down.
`01 23 45 | 00 05 | 67 89 AB CD EF`

The first three bytes is a `24 bit` number for the  target `offset`, the next two bytes is a `16 bit` number for the size of the data. The final series of bytes is the data of which it's length is described by the `16 bit` size number.

**Example of an RLE Instance:**

`01 23 45 00 00 FF FF 64`

The first three bytes are still the `24 bit` target `offset` however you may notice the `16 bit` size bytes are equal to zero, indicating that the data is zero in length. However, when the size is equal to zero we treat this is an `RLE flag` indicating that this `instance` behaves differently.

 We read past the two size bytes and take the next `two bytes` as a `16 bit` number describing the `hunk length` of the `RLE ` instance. The last byte is the `hunk data` and will be repeated until it's length is equal to the `16 bit` "hunk length". 

Spaces in-between offsets beyond the size of the original file size are expected to be zeroes, drastically reducing file size and likely complexity too leading to faster handling. When not storing past the original file the space in between offsets stores the original file contents which are not included in the `ips` for both efficiency and integrity.

### How to read/apply one?

Here it will be demonstrated in very simple Python, but annotated well even when the code is verbose.

```python
def apply(base : bytes, patch : bytes) -> bytes:
	patch = patch[5:-3]			#trim header and footer
	changes = {}				#dictionary to store diffs
	count = 0				#create variable used to track progress in "patch"
	while count != len(patch):		#Until we have read the last byte
		offset = patch[count:count+3]	#read next 3 bytes
		offset = int(offset.hex(),16)	#convert to 24 bit integer
		count += 3	
		size = patch[count:count+2]			#read next two bytes
		size = int(size.hex().16)			#convert to 16 bit integer
		if not size:					#if RLE flag set
			count += 2
			size = patch[count:count+2]		#Acces RLE Length bytes
			size = int(size.hex(),16)		#convert to 16 bit number
			count += 2
			data = patch[count:count+1]
			changes[offset] = (size,data)		#Store RLE instance with offset as key
		else:
			data = patch[count:count+size]
			changes[offset] = data 			#Store noRLE instance with offset as key
			count += size
	output = b""
	for offset in changes:
		if offset < len(base):				#if we are still overwriting
			output += base[len(output):offset]	#Copy base until diff start
		else:
			output += b"\x00" * (offset-len(base))	#Write zeroes until diff start
		if isinstance(changes[offset],tuple):
			output += changes[offset][0]*changes[offset]*1
		else: output += changes[offset]
	output += base[len(output):]				#if we have not wrote up to base, then do so
	return output
```
The code above accepts two `bytes` objects and will return ` byets` object which could be parsed into a `file` object.  If you only needed this data for patching then you could :
```python
def patchfile(modfile,basefile,outfile):
	def get(File):
		with open(File,"rb") as f:
			return f.read()
	with open(outfile,"wb") as f:
		f.write(patch(get(base),get(mod)))
```
However as `patchlib.ips` is a module, usage is determined by the user and therefore despite the applications beyond standard usage being nothing short of eccentric does not invalidate the intentions. This is where `patchlib.ips` exceeds `ips.py`.

**How does `ips` building work?**

`ips` constructing is much more detailed than `ips` applying,  as we have to account for the following things:

- `ips` files *should* contain minimal original data.*
- `ips` files *should* not attempt to make an impossibly large file.**
- `ips` files *should* prefer `rle` unless setup is too costly.***
- `ips` files *must* write to the last byte of the new file if bigger , even if zero.

`*` *This does not mean that it won't work, it just means that you may end up creating an unnecessarily large file that contains potentially sensitive data*

`**` *By default in `patchlib` it is set to `16,777,215 bytes` ( 16.7 MB) however `ips` may reach up to `16,842,750 bytes` by setting `legacy` to  `False`*

`***` *This is merely optimization, no `ips` has to contain `rle` however it should be noted that it is only optimal if the `rle` is of length `9` or higher.*

Now that you know the rules, we can begin to create an `ips` file.
```python
def build(base : bytes, target : bytes) -> bytes: 
	patch,count = b"", 0   
	
	#Lambdas for operation viability checks
	viability = lambda offset, dist: target[offset].to_bytes(1, "big")*dist == target[offset : offset + dist]
	compare = lambda offset: (base[offset] != target[offset]) if offset < len(base) else True 

	def rle():		#function for processing rle data
		length = 9
		while compare(count + length) and count + length < len(target) and viability(count, length): length += 1
		return length - 1

	def norle():			#function for processing rle unviable data
		length = 1 
		while compare(count + length) and count + length < len(target) and not (viability(count + length, 9) and all(compare(count + length + r) for r in range(9))): length += 1
		return length

	#while we have not compared the final byte
	while count < len(target):
    
		#if we are comparing the final byte
	    if count == len(target)-1:
	    patch += count.to_bytes(3, "big")+b"\x00\x01"+target[count].to_bytes(1, "big")
		count += 1
        
        #if we have unncessary data
        elif base[count] == target[count] if count < len(base) else target[count] == 0:
			while (base[count] == target[count] if count < len(base) else target[count] == 0) if count < len(target) - 1 else False: count += 1 
        
		#now that we have our diff
		else:
			#determinte rle viability
			isrle = viability(count, 9) and all(compare(count + r) for r in range(9)) 

			length = [norle,rle][isrle]()	#retrieve length to store
			
			#while length is impossible for a singular instance
			while length > 0xFFFF:
				if isrle: patch += count.to_bytes(3, "big")+b"\x00\x00\xff\xff"+target[count].to_bytes(1, "big") 
				else: patch += count.to_bytes(3, "big")+b"\xff\xff"+target[count:count+0xFFFF]
				count += 0xFFFF 
				length -= 0xFFFF
               
            #if data was not a multiple of 0xFFFF  
			if length:
				if isrle: patch += count.to_bytes(3, "big")+b"\x00\x00"+length.to_bytes(2, "big")+target[count].to_bytes(1, "big") 
				else: patch += count.to_bytes(3, "big")+length.to_bytes(2, "big")+target[count:count+length] 
				count += length

    #return data
	return b"PATCH"+patch+b"EOF"
```

This is the *best* `ips` construction code in terms of minimal output and is very optimized.
```python
def makepatch(basefile,targetfile,outfile):
	def get(File):
		with open(File,"rb") as f:
			return f.read()
	with open(outfile,"wb") as f:
		f.write(build(get(basefile),get(targetfile)))
```

### Why do we sometimes use other patching filetypes?
`bps` for example, uses variable width offsets, and instead of immediate replacement it uses "actions" to move the data and perform selective "range" overwrites in order to achieve a goal with *variable* scope. `ips` has a reach of `16,842,750 bytes`, however a true legal `ips` could not write beyond the `24 bit` maximum and therefore the maximum reach is truly `16,777,215 bytes`.

`ips` also is horribly inefficient at patching large files, some files may contain duplicates of the base code, which is not just horribly inefficient but also provides a security risk for the original file contents.  A simple `ips` integrity checker could be constructed to compare base contents to patch contents to see what resemblance there is .

In conclusion, `ips` is designed for an older generation of consoles that were small and simplistic, as the scope of technology gradually increases we may see `bps` become irrelevant. Currently, and for much time, it is irrational to assume that `bps` can be made redundant however as it can reach up to a theoretical `2 exabytes` in reach. 
### Why do we still use `ips` if better filetypes exist?
Easiest question of them all, `ips` was just there when it needed to be. Because of `ips`'s common usage and popularity when ROMhacking was more niche than it was the filetype has been the face of early ROMhacking, `ips` is actually quite space efficient for most of these hacks, it fit's its scope perfectly. 

In some cases, you may opt for `bps` over `ips` if the scope of the project would benefit from it, however for minor edits within the size of the base file there is commonly zero reason not to choose `ips` unless the file you are modding requires a higher reach. 
### Why should I use `iplsuna` over `ips.py`?
The main reason you should choose `patchlib` over `ips.py` is because *it does what ***every*** other **advanced** patching tool does*. After being passed the raw contents of an `ips` or initialising a blank canvas, `patchlib` offers **total** control of the `ips`.  Each instance (diff) has the `size`, `data`, `rle flag`, and `diff-reach` stored in the `instance` class as well as a `name` attribute which can be used to annotate an `ips`.

The benefit to all of this is that now we can *smartly* interact with the instances, we can access them with a variety of functions such as `get`, `range`or by accessing the `instances` attribute within the `ips` class which stores each `instance` by order of `offset`. We can also modify the individual `instance` with the `modify` method.

Moreover, the project is being actively worked on - and updates and new features should be expected. The code exceeds all known IPS tools and is not even at a release build yet, and it has full docs on the [`PyPI`](https://pypi.org/project/patchlib/) and active developers in immediate contact on the [Discord](https://discord.com/invite/3DYCru4dCV)!
### Should I make my own `ips` handling tool?
There is very minimal reason to do this. As it stands, even when `ips` filetypes are being manipulated at a deep level, the tools provided are often not even fully used as rarely does the user exceed common `building` and `applying`. There is generally a surplus of tools, should you create your own `ips` tool there should be a reason for this, `patchlib`'s existence is to provide total control in a `Python 3.7` runtime or above.

`JIPS` is forgivable as it runs in a Java runtime, meaning that it can run on devices that do not support `Python 3.7` or `Python` at all! Because `JIPS` uses `Java`, the whole ideology being that it can run in *any* environment, this tool is very helpful to those who do not have an Operating System which any dedicated tool can support.

The same *would* go for `ips.py` if `patchlib` did not render it redundant.
If you wish to make a tool, ensure that the benefits are not found immediately in someone else's tools alone.  Once you can confirm there is a point to doing this baring scope, usability and cause, making an `ips` handler makes complete sense.
### Can I contribute towards `patchlib`?
Yes! `patchlib` GitHub allows for forks to be made and anyone with some `Python` skill can be included in the Project! In fact, there are many elements of the project left **totally** untouched that you could begin working on! If you are interested feel free in contacting on the [Discord](https://discord.com/invite/3DYCru4dCV)!
### Is it not better just to make your own filetype?

This should be overall somewhat discouraged for these reasons:

- `ips` is standardized, people may not want to use your files/tools
- It is quite likely that `bps` could solve this, people *will* use that instead
- It creates some sort of proprietary sense to it, which may deter users.
- If tool sharing is too slow for demand, users may share original files

If people do not want to use your tools then the project's popularity will be stunted, if people construct a `bps` between the base and result file then nobody will feel obliged to use *your format or tool*. In the world of common base files it is natural to assume a universal format for manipulation, for this we opt for universal filetypes, limiting control only works for immediate distribution.
	
