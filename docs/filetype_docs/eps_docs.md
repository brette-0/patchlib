## **Brette's Consumable EPS Filetype Docs**

### What is EPS?

`EPS` was designed by Brette, a hybrid mix of byuu's `BPS` and the fabled `IPS`. Displeased with the production-oriented exclusivity of `BPS` as a result of context-less pointers and the soft `24 bit` upperlimit of `IPS`, Brette began scheming of ways to bring the developmental patch methodology for ROMhacking to higher bit systems. 

**Currently there are no systems that support EPS**

`EPS` was developed in tandem with the `patchlib` project by Brette, the only tool for it is `patchlib.eps` and can be accessed with `pip install get-patchlib`. This tool allows for total control over the patch contents, patch creation and patch application for any system that can run a Python 3.9 environment. As of writing this, ROMPatcherJS does not offer support for `EPS`.

### `variable-width decoding`
`bps` uses a simple method to encode numerical information called 'variable-width encoding. In a series of bytes, the MSB is a termination flag and remains unset whilst the data is being streamed into an output value. Once the MSB of a byte is set, that byte then contains the last value for that encoded number. Below is a method of how it works, however in production we access the entire patch by reference.
```python
def decode(encoded : bytes) -> int:
    if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")
    number,shift = 0, 1
    for byte in encoded:					    #for each byte in our given data
        number += (byte & 0x7f) * shift		    #increase number by data bits
        if byte & 0x80: return (number>>1)*(-1 if number & 1 else 1) if signed else number				    #return if termination bytes set
        shift <<= 7
        number += shift
```
### `variable-width encoding`
Here it entirely appropriate to pass an integer by value, this is the simple process to encode numerical information with our format, as you may expect it is merely bit masking and bit shifting with context based bit setting. 
```python
def encode(number : int) -> bytes:
    encoded = bytes()						    #Create empty bytes object to store variable-width encoded bytes
    while True:									#Until we are finished
        x = number & 0x7f						#Using the 7 LSB of the number
        number >>= 7							#And removing such data
        if number: 								#If there is still source data to read
            encoded += x.to_bytes(1, "big")	    #Append the data to our bytes object
            number -= 1							#Decrement by one to remove ambiguity
        else: 
	        #set termination bit and return
            return encoded + (0x80 | x).to_bytes(1, "big")
```

### Header Extraction

The `EPS` header is quite simple, first we have a string reading `EPS0`, then we have an encoded number specifying the size of the `data_bank`, from this offset onwards the specified length is the `data_bank` which is indexed by the instances.

### Data Bank

`EPS`, unlike `BPS` does not store the information for each 'action', instead it specifies what new data will be used in the 'data bank' which is just a large array of bytes for all instances. This is to reduce the size of pointers, thus reducing the size of the patch.

### Applying

```py 
def apply(source : bytes, patch : bytes)->bytes:
	def decode():
		nonlocal patch
		number,shift = 0, 1
	    for byte in patch:
	        number += (byte & 0x7f) * shift
	        if byte & 0x80: return (number>>1)*(-1 if number & 1 else 1) if signed else number
	        shift <<= 7
	        number += shift

	patch = patch[4:]
	bank_size = decode(patch)
	data_bank = patch[:bank_size]
	patch = patch[bank_size:]
	
	target = bytes()
	offset = 0
	while patch: 
		length = decode() 
		if length: 
			# this is patch information
			pointer = decode() 
			if pointer & 1:
				# this is copy function
				"""
				perform a target_copy style move (only should be generated post source)
				from offset added this signed value (next bit) 
				"""
				relative = (pointer >> 2) * (-1 if pointer & 2 else 1)
				# perform target_copy loop from (offset + relative) to (offset + relative + length)
			else: 
				# this is a read function
			target += bank[pointer : pointer + length]
		else: 
			# this is a sign of no-data 
			length = decode()
			target += source[offset : offset + length]
			offset += length
		
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
However as `patchlib.eps` is a module, usage is determined by the user and therefore despite the applications beyond standard usage being nothing short of eccentric does not invalidate the intentions.

**How does `eps` building work?**

Overview

- Condition 1
- Condition 2
-  Condition 3

`*` *Explanation 1*

`**` *Explanation 2*

`***` *Explanation 3*

Now that you know the rules, we can begin to create a `eps` file.
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

### Why should I use this patch type?
Should you want to share a single feature for other people to use in their hacks, you need no longer share project source, or rely on the user to understand how to implement your custom code. Any ROM changes that you make outside of the range of `IPS` `EPS` is there for you. Unlike `BPS`, `EPS` uses zero validation processes, this means that at no point will earlier modifications throw a checksum error when applying an `EPS` patch.

### Should I use `EPS` for production as well?
Absolutely not. `EPS` files are optimized only to the extent it follows the filetype's golden rule. *do not copy source information*. This simple limitation, despite being ideal for developmental patches, is a drawback to creating optimized patch sizes. If you are simply wishing to share a finished project, please use `BPS` over anything else.

### Should I make my own `eps` handling tool?
I encourage it. Some simply do not wish to use a python environment, or prefer a comfy GUI over a beginner-intimidating CLI. Seeing this used  server-side or rewrote faster in Java would be excellent. However, this filetype is merely complimentary to the abundances of options out there so it should be no priority.



### Can I contribute towards `patchlib`?
Yes! `patchlib` GitHub allows for forks to be made and anyone with some `Python` skill can be included in the Project! In fact, there are many elements of the project left **totally** untouched that you could begin working on! If you are interested feel free in contacting on the [Discord](https://discord.com/invite/3DYCru4dCV)!

### Will you ever updated `EPS`?
It is not unlikely that at some yet unforeseen point in the future some redundancy may be found in `EPS`, for `IPS` its stating the entire offset instead of using relative offsets. For `BPS` its the entire existence of `target_read`. While no doubt these choices made sense - it does not mean that something else more sensical could have been substituted.
### Should I make my own filetype too?

While I have discouraged this in the other docs on this page, I bear exemption on this occasion due to discovering a purpose for this patch to exist - outside of what has already been fulfilled with other systems.
- existing formats comply to methodology standards, if there is no demand the project will remain unknown.
- Your task may already be solved with a pre-existing solution.
- It creates some sort of proprietary sense to it, which may deter users.
- If tool sharing is too slow for demand, users may share original files

If people do not want to use your tools then the project's popularity will be stunted, if people construct a `bps` between the base and result file then nobody will feel obliged to use *your format or tool*. In the world of common base files it is natural to assume a universal format for manipulation, for this we opt for universal filetypes, limiting control only works for immediate distribution.