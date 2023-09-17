# `patchlib`
`patchlib`  is a library of tools for total control of the fundamental elements of each `patch` filetype, and is split into several packages, each documented in detail in this repository, and installed on: [PyPi]( https://pypi.org/project/patchlib/)

Or can be installed with:

|Windows|Posix / Unix|
|--|--|
|`pip install get_patchlib`  | `pip3 install get_patchlib` |
 - *Intended for Python 3.7 and above*
 - Uses [`importlib`](https://docs.python.org/3/library/importlib.html) for complete importing
 - Uses [`zlib`](https://docs.python.org/3/library/zlib.html) for checksum comparison
 - Currently can only use `ips` and partially `bps` files.
 - [Interactive Docs](https://patchlib.readthedocs.io)

|Name | package |Docs| Version| Module Size | File Docs|
|--|--|--|--|--|--|
|IPS|[`patchlib.ips`](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips.py)| [patchlib.ips](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/package_docs/patchlib.ips_docs.md) |0.9|16.464 KB |[IPS](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/filetype_docs/ips_docs.md) |
|BPS|[`patchlib.bps`](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/bps.py)|[patchlib.bps](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/package_docs/patchlib.bps_docs.md)|0.6|11.2 KB|[BPS](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/filetype_docs/bps_docs.md)
|Xdelta|[`patchlib.xdelta`]()|Not yet|None|None|None
|PPF|[`patchlib.ppf`]()|Not yet|None|None|None
|UPS|[`patchlib.ups`]()|Not yet|None|None|None

|APS|[`patchlib.aps`]()|Not yet|None|None|None
|RUP|[`patchlib.rup`]()|Not yet|None|None|None
|NPS|[`patchlib.nps`]()|Not yet|None|None|None
|Luna|[`patchlib.eps`]()|Not yet|None|None|None

Using `import patchlib` will install all packages with the `importlib` module. `patchlib` provides no context abundant methods and relies on the package being specified.


# Patching and its significance

In the ever expanded world of the internet what may have been unique becomes shared, what may have been niche is popularized and communities of all different sizes collide and integrate with varying level of harmony in the great efforts to harvest the results of their labor and thrive amongst their fellow hobbyists and sometimes even more.

Since the great invention of it, Video Games have amassed unimaginable funding due to its unaccountable popularity. Whilst this was not always so, even when Video Games were considered no more than a toy - the passionate of them created communities of their own. Some of them tried to beat the game as fast as possible, some of them translated the game into other languages, some of them documented the game.

Some of these early video-game players were of a technical mind and pursued how the game functioned. Perhaps in the form of a cheat system, trainers, or early emulators. However the legality of this all had not always been the same. While Game Genie had its own controversy, that had not been because Nintendo had been fearful - rather the parent company of Game Genie did.
 
 Trainers, however, are an entirely different situation. Trainers were modified versions of games with built-in cheats that could be accessed from a menu before the game loaded. These were created before these patching systems were invented - and thus games were pirated extensively via online shell based chatrooms of the early internet.

That's right. Video games have been pirated even when the only commercial internet service was dial up. This was likely for two reasons: Piracy's objective of getting something for free and the built-in cheats allowing for a new game experience. Finally, whilst emulators have always been in something of a controversy - early emulators often did not have this issue. 

The NES for example, had no real protection against emulators - in fact, the console itself had no real way of detecting a bad cartridge. Whilst the entire point of the CIC lockout chip was to prevent unauthorized cartridges from running on the system. CIC10 was defeated in numerous different ways, a bypass chip now exists in mass production. Rerouting pins before they even his the cartridge as a hardmod exists as a solution. 

Even historically, Atari had committed an act of fraud in order to pirate Nintendo's CIC10 BIOS. After the NES and Gameboy, video game companies at this time began working on ways to detect emulator usage in order to circumvent piracy. Note this, emulation and piracy are too different things. 

The calls to defeat emulation are purely economic, having the game run on a device that is not the platform it was intended for means that the platform may not be purchased. Furthermore, these platforms intended to run this software may contain security checks to prevent piracy or modifications that would violate the TOS. 

Emulation enables piracy. It is that simple. For this, major companies endeavor persistently to shut down emulation. Video game producers will also implement whatever methods they can to prevent the game working on an emulator, these methods have also been used to detect pirated copies. For example, Banjo Tooie for the Nintendo 64 and Spyro for the Playstation.

However, currently emulation and ROMhacking are legal. Video game producers are at leisure to take down anything that uses their source material, and distributors such as Nintendo are expected to take down anything that may threaten their registered developers.

While its legal, that does not mean that does not face legal scrutiny. In order to ROMhack in a way that complies with the law, we develop are tools and distribute are results in a way that does not commit any crimes. Dolphin, the Wii and Gamecube emulator, did not do this. Dolphin stored the Wii's decryption keys inside the source code as constants. In short, Dolphin included sensitive Nintendo material and this led to Nintendo ordering Steam to deregister Dolphin's Steam port.

The means to safely distribute legal game modifications is a patch file. Note that a patch file may contain sensitive data, should you complete the pointless task of building a patch file for the Legend of Zelda for Super Mario Bros then that patch enables piracy and sharing that would be illegal as it contains an extensive amount of pirated content.

The grey area appears once you accept that how much 'data' you can have before its plausibly considered someone else's copyrighted works is not a fixed point. Should there be reason to concern the patch will likely be taken down. Should you wish to take legal action you may - however it is quite likely that you will not win your case.

Assuming you modify your legally dumped copy of a game and you have modified it with your own or public assets, you will feel tempted to share it with your friends. Should you share the ROM (the game file) you have committed an act of piracy, delete the file and think about what your parents would think about you.

Once you've done that, its encouraged to share your works with your community in the form of a legally safe patch file. What patch file you choose is entirely up to you. However here is an overall evaluation of the types. 

## International Patching System (IPS)

This patching system is the oldest, should the modifications be lightweight it should create a relatively small patch file. Should your ROMhack be content rich or larger than the original file the IPS may end up being bigger. 

For more information on IPS click here

## Beat Patching System (BPS)

This patching system is incredibly efficient compares to IPS. Reducing output file sizes often threefold. Whilst the target file and patch size are inevitably directly proportional, instead of their relation being exponential - BPS becomes more efficient with a larger result file. 

