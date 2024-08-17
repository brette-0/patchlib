Beat Patching System 
####################

What is BPS?
~~~~~~~~~~~~

``bps`` was designed by Emulator enthusiast `byuu <https://www.romhacking.net/forum/index.php?topic=32951.0>`__, who, with this solution, created the standard for patch files in the ROMhacking community. While in truth a successor to `ups <h>`__ , ``bps`` offers a level of sophisticated versatility that was not needed when ``ips`` was suitable for known ROMhacking scopes.

``bps`` is designed for mainly three reasons, the first being that ``ips`` had a soft upper limit of about ``16 MB`` and therefore larger games would be unmodifiable if it were not for a successor. Secondly, ``bps`` does not *need* to store any ``source`` data beyond original file offset as it refers to ``source`` during patching. Finally, ``bps`` offers more efficient patching with incredibly low filesizes.

**Popular IPS tools include:**
 - `beat <https://www.romhacking.net/utilities/893/>`__
 - `Multipatch <https://www.romhacking.net/utilities/746/>`__
 - `Floating IPS <https://www.romhacking.net/utilities/1040/>`__

byuu developed `beat <https://www.romhacking.net/utilities/893/>`__ alongside their ``bps`` filetype intended to be used in a 32bit Windows environment. `Multipatch <https://www.romhacking.net/utilities/746/>`__ was designed for MacOSX and supports many patch filetypes including ``bps``. ``bps`` does not have a long history like ``ips`` and much less tools has been developed as of writing this in 2023. As of ``2023`` `Floating IPS <https://www.romhacking.net/utilities/1040/>`__ is the most popular bps tool and includes ips as well and is generally considered one of the best patch tools there is.


`ROM Patcher JS <https://www.marcrobledo.com/RomPatcher.js/>`__, however eradicates the usage of executable "diff" appliers/makers as the tool is made entirely in JavaScript and therefore can use mod files and base files in a browser. (The Exception being ``xdelta`` files that use ``Xdelta3`` format which requires an x64/ARM environment that most web services cannot offer)

``variable-width decoding``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bps`` uses a simple method to encode numerical information called 'variable-width encoding. In a series of bytes, the MSB is a termination flag and remains unset whilst the data is being streamed into an output value. Once the MSB of a byte is set, that byte then contains the last value for that encoded number. Below is a method of how it works, however in production we access the entire patch by reference.

.. code-block:: python

	def decode(encoded : bytes) -> int:
		if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")
		number,shift = 0, 1
		for byte in encoded:					    #for each byte in our given data
			number += (byte & 0x7f) * shift		    #increase number by data bits
			if byte & 0x80: return (number>>1)*(-1 if number & 1 else 1) if signed else number				    #return if termination bytes set
			shift <<= 7
			number += shift

``variable-width encoding``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here it entirely appropriate to pass an integer by value, this is the simple process to encode numerical information with our format, as you may expect it is merely bit masking and bit shifting with context based bit setting. 

.. code-block:: python

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
				reurn encoded + (0x80 | x).to_bytes(1, "big")

**Header and Footer extraction**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The header simply stores the string ``BPS1`` to indicate filetype, followed by three encoded numbers for the expected sizes of (in chronological order): the desired source file, the desired target file, the contained metadata. Whilst not entirely common, a patch may store a metadata file which by spec should be an ``xml``, however no ``xml`` functionality has been utilized and the metadata can be whatever filetype the user decides. The footer is simpler yet, it stores three small endian checksums for: the source file, the target file, the patch file inclusive of the previous two checksums. 

# Patch Actions

Unlike ``ips``, ``bps`` does not simply write patch data from the offset to the target - but rather the instructions on how to create the result data from repositioned source, written and current target data. We call these ``actions`` There are four of these which vary in functionality which all are called from one main function used to determine the required operation.

**How to read and apply one?**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Here it will be demonstrated in very simple Python, but annotated well even when the code is verbose.

.. code-block:: python 

	def apply(patch : bytes, source : bytes) -> bytes:
		def decode():
			nonlocal patch
				if not isinstance(encoded,bytes): raise TypeError("Encoded data must be bytes object")
				number,shift = 0, 1
				for byte in encoded:
					number += (byte & 0x7f) * shift
					if byte & 0x80: return number
					shift <<= 7
					number += shift
		patch = patch[4:-12]
		output_offset = source_offset = target_offset = 0
		while patch:
			length = decode()
			action = length & 3
			length = (length >> 2) - 1
			if action == 0:
				target += source[output_offset : output_offset + length]
			if action == 1:
				target += patch[:length]
				patch = patch[length:]
			if action == 2:
				relative = decode()
				relative = (-1  if  relative  &  1  else  1) * (relative  >>  1)
				source_offset += relative 
				target += source[source_offset : source_offset + length]
				source_offset += length 
			if action == 3:
				relative = decode()
				relative = (-1  if  relative  &  1  else  1) * (relative  >>  1)
				target_offset  += relative 
				if  target_offset + length <  len(target):
					target += target[target_offset : target_offset + length]
				else:
					loop = target[target_offset:]
					target +=  b"".join([loop for x in range(length // len(loop))]) + loop[:length % len(loop)]
				target_offset += length 
			return target

The code above accepts two ``bytes`` objects and will return `` bytes`` object which could be parsed into a ``file`` object.  If you only needed this data for patching then you could :

.. code-block:: python
	
	def patchfile(modfile,basefile,outfile):
		def get(File):
			with open(File,"rb") as f:
				return f.read()
		with open(outfile,"wb") as f:
			f.write(apply(get(base),get(mod)))

However as ``patchlib.bps`` is a module, usage is determined by the user and therefore despite the applications beyond standard usage being nothing short of eccentric does not invalidate the intentions.

How does ``bps`` building work?
-------------------------------

``bps`` constructing is much more detailed than ``bps`` applying,  as we have to account for the following things:

- ``target_copy`` overlapping checks must always be checked first
- ``source_read`` takes priority over ``source_copy`` only if optimal.
-  Electing the closest relatives allows for smaller pointers.

``*`` *byuu's method to obsoleting RLE in patching was self-referential ``target_copy`` actions. Allowing the newly generated data to be accessed immediately for the output.*

``**`` *while it may initially seem obvious, if more data can be accessed elsewhere for this offset then ``source_read`` is unpreferable, however if this is not the case then ``source_read`` should then be chosen due to it being pointer-less*

``***`` *If the theory is correctly implemented, the patch will mostly be relative copy functions. Through understanding that segments of data will be repeated throughout the patch - choosing an optimal path reduces file size greatly.*

 **Currently** ``patchlib.bps`` **has no short term plans for a build method.**

Why do we sometimes use other patching filetypes?
-------------------------------------------------

``ips`` was the original patch filetype, however it complied to outdated hardware limitations that makes it often unsuitable for larger tasks. ``bps`` is not the immediate successor to ``ips``, but it is the successor to ``ups`` also made by byuu. 

Currently, I do not have the theory on UPS or Xdelta, so no information in relation to these can be answered from me.

Should I use Xdelta over ``bps``?
---------------------------------
While my knowledge on Xdelta is essentially none, ``bps`` has some advantages over Xdelta - being that ``bps`` under no circumstances will demand a ``64 bit`` environment due to Xdelta3's ``64 bit`` exclusive method for encoding. ``bps`` has theoretical functionality for systems with a higher bitsize than ``64`` despite working on lower systems.

### Should I make my own ``bps`` handling tool?
As of this being written up there are not too may ``bps`` handlers compared to the likes of ``ips``. If there is some way, be it operating system or technical feature, that ``bps`` has been left unfulfilled it may be logical to create these tools.



Can I contribute towards ``patchlib``?
--------------------------------------
Yes! ``patchlib`` GitHub allows for forks to be made and anyone with some ``Python`` skill can be included in the Project! In fact, there are many elements of the project left **totally** untouched that you could begin working on! If you are interested feel free in contacting on the [Discord](https://discord.com/invite/3DYCru4dCV)!
### Is it not better just to make your own filetype?

This should be overall somewhat discouraged for these reasons:

- ``bps`` is standardized, people may not want to use your files/tools
- It is quite likely that ``bps`` could solve this, people *will* use that instead
- It creates some sort of proprietary sense to it, which may deter users.
- If tool sharing is too slow for demand, users may share original files

If people do not want to use your tools then the project's popularity will be stunted, if people construct a ``bps`` between the base and result file then nobody will feel obliged to use *your format or tool*. In the world of common base files it is natural to assume a universal format for manipulation, for this we opt for universal filetypes, limiting control only works for immediate distribution.
