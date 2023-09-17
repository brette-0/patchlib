# `patchlib`
`patchlib`  is a library of tools for total control of the fundamental elements of each `patch` filetype, and is split into several packages, each documented in detail in this repository, and installed on: [PyPi]( https://pypi.org/project/patchlib/)

Or can be installed with:

|Windows|Posix / Unix|
|--|--|
|`pip install get_patchlib`  | `pip3 install get_patchlib` |
 - *Intended for Python 3.7 and above*
 - Uses [`importlib`](https://docs.python.org/3/library/importlib.html) for complete importing
 - Uses [`zlib`](https://docs.python.org/3/library/zlib.html) for checksum comparison
 - Currently can only use `ips` files. *(`bps` is currently in-dev)*
 - [Interactive Docs](https://patchlib.readthedocs.io)

|Name | package |Docs| Version| Module Size | File Docs|
|--|--|--|--|--|--|
|IPS|[`patchlib.ips`](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips/__init__.py)| [patchlib.ips](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/package_docs/patchlib.ips_docs.md) |0.9|16.464 KB |[IPS](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/filetype_docs/ips_docs.md) |
|BPS|[`patchlib.bps`](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/bps/__init__.py)|[patchlib.bps](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/package_docs/patchlib.bps_docs.md)|0.6|11.2 KB|[BPS](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/filetype_docs/bps_docs.md)
|Xdelta|[`patchlib.xdelta`]()|Not yet|None|None|None
|PPF|[`patchlib.ppf`]()|Not yet|None|None|None
|UPS|[`patchlib.ups`]()|Not yet|None|None|None
|APS|[`patchlib.aps`]()|Not yet|None|None|None
|RUP|[`patchlib.rup`]()|Not yet|None|None|None
|NPS|[`patchlib.nps`]()|Not yet|None|None|None
|Luna|[`patchlib.eps`]()|Not yet|None|None|None

Using `import patchlib` will install all packages with the `importlib` module. `patchlib` provides no context abundant methods and relies on the package being specified.
