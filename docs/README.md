# `patchlib`
`patchlib`  is a library of tools for total control of the fundamental elements of each `patch` filetype, and is split into several packages, each documented in detail in this repository, and installed on: [PyPi]( https://pypi.org/project/patchlib/)

Or can be installed with:

|Windows|Posix / Unix|
|--|--|
|`pip install get_patchlib`  | `pip3 install get_patchlib` |
 - *Intended for Python 3.7 and above*
 - Uses [`importlib`](https://docs.python.org/3/library/importlib.html) for complete importing
 - Currently can only use `ips` files.
 

|Name | package |Docs| Version| Module Size | File Docs|
|--|--|--|--|--|--|
|IPS|[`patchlib.ips`](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips/__init__.py)| [patchlib.ips](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/patchlib.ips_docs.md) |0.9|17 KB |[IPS](https://github.com/BrettefromNesUniverse/patchlib/blob/main/docs/ips_docs.md) |
|BPS|[`patchlib.bps`]()|Not yet|alpha|5.85 KB|None
|Xdelta|[`patchlib.xdelta`]()|Not yet|None|None|None
|PPF|[`patchlib.ppf`]()|Not yet|None|None|None
|UPS|[`patchlib.ups`]()|Not yet|None|None|None
|APS|[`patchlib.aps`]()|Not yet|None|None|None
|RUP|[`patchlib.rup`]()|Not yet|None|None|None
|NPS|[`patchlib.nps`]()|Not yet|None|None|None
|Luna|[`patchlib.luna`]()|Not yet|None|None|None

Using `import patchlib` will install all packages with the `importlib` module. `patchlib` provides no context abundant methods and relies on the package being specified.

`Luna` serialized class handling may be implemented at a later point in time once enough of the crucial patch filetypes have been completed.

[docs](https://github.com/BrettefromNesUniverse/patchlib/tree/main/docs) applies only to the ***[working build](https://pypi.org/project/patchlib/)** and therefore may not reflect the **[open source versions](https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/).*** Contributions are open an encouraged, and will be release once the open build leaves exerpiment phase.
