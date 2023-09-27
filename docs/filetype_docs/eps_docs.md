## Brette's Consumable EPS Filetype Docs

### What is EPS?

The `EPS` or `Enhanced Patching System` filetype was created in 2023 to express "diffs" between a controlled `base` file and a resultant `target` file similarly to `ips` however optimized and deconstricted to immitate the versatility of `bps`. 

The `EPS` filetype was developed by Brette who wished to develop a developmental-patch methodology to ROMHacker for higher bit systems.  As the upperlimit of `ips` and the context-ignorant attribute of `bps` made development patches harder to supply for Higher bit systems.

**Currently the only known `eps` tool is [`patchlib.eps`]()**

 - `pip install patchlib`
 ```py
import patchlib.eps as eps
```

As of writing this, [ROM Patcher JS](https://www.marcrobledo.com/RomPatcher.js/), does not offer support for `eps` filetype - however a `JS eps` handler is entirely possible and may someday be integrated into it.

### How does it work?

`eps`, unlike `bps` does not bring data from other offsets into current offets. This is because doing that means that the context of the information is lost - this means that the pointers are set up to expect the same input each time and not complying to this will result in catastrophic failure.

Whilst you could use create a `bps` file that does not perform copy actions - that would be inefficient due to how `bps` is set up. The gift of `ips` was specified offsets, meaning that the length of original data never meant to be specified. 

However, the year when making this is 2023 and we have some new tricks. For example: instead of storing offset, store length with a flag to use source data. Instead of storing new data for every non-source write, store a pointer adjustor to access a shared library of patch data.

**Example of a skip:**

`36 ae`

This here is a variable-width encoded length, once you decode it you are presented with `0x6072`. This here is divided by two to equal 12344 and the target flag unset. Which means that we will use this length plus one as how many source bytes we will use.

**Example of a withdraw:**

`0b e9`

This here is also variable-width, and it is decoded and handled in the same fashion as a skip. *however*, since the target flag is set we know that this then is a bank withdrawal. The next value is a signed variable width pointer adjustor that will set the beginning offset for the data we will take. Whilst the length has one added to it, at this point we subtract the one and if it is zero. We loop the byte for the specified length at this offset. 

### How to read/apply one?

Here it will be demonstrated in very simple Python, but annotated well even when the code is verbose.

```python
def apply(source, patch) -> bytes:
	offset = pointer = adjustor = 0
	target = bytes()
	def decode(): pass 
	bank = patch[:decode()]

	while len(patch):
		length = decode()
		if length & 1: 
			length >>= 1
			length += 1
			adjustor = decode()
			adjustor = (adjustor >> 1) * (-1 if adjustor & 1 else 1)
			pointer += adjustor
			if length: 
				target += bank[pointer : pointer + length] 
			else:
				length = decode() + 1
				target += bank[pointer] * length
		else:
			target += source[offset : offset + (length >> 1)]
	return target
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
However as `patchlib.eps` is a module, usage is determined by the user and therefore despite the applications beyond standard usage being nothing short of eccentric does not invalidate the intentions. This is where `eps` exceeds `bps`.

**How does `eps` building work?**

Discuss.

- condition 1*
- condition 2**
- condition 3***

`*` *Explanation 1*

`**` *Explanation 2*

`***` *Explanation 3*

Now that you know the rules, we can begin to create an `eps` file.
```python
def build(base : bytes, target : bytes) -> bytes: 
	return
```

Discuss.
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
### Why did you make your own filetype?

Despite this being overall somewhat discouraged, I felt that:

- `eps`'s use is more niche than other patches, meaning that its use may suffiec its demand - albeit little.
- No other patching filetype could solve this issue
- The propriety arguement is invalid as its goal is unique to others, should a sucessor be made then so be it.
- There is no hesitation in tool usage.

If people do not want to use your tools then the project's popularity will be stunted, however this really only applies to production patches - this is what we call a developmental patch. A developmental patch is a patch that introduces a new feature in order for a ROMhacker to include in their project. Despite `ips` being capable of doing this - it has its awful limitations. 