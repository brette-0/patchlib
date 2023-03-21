# IPSLuna
`ipsluna`  is a library of tools for total control of the fundamental elements of each `patch` filetype, and is split into several packages, each documented in detail in this repository, and installed on: [PyPi]( https://pypi.org/project/ipsluna/)

Or can be installed with:

|Windows|Posix / Unix|
|--|--|
|`pip install ipsluna`  | `pip3 install ipsluna` |
 - *Intended for Python 3.7 and above*
 - Uses [`ctypes`](https://docs.python.org/3/library/ctypes.html) for unsigned upperlimit retrieval
 - Uses [`Importlib`](https://docs.python.org/3/library/importlib.html) for complete importing
 - Currently can only use `ips` files.
 

|Name | package |Docs| Version| Module Size | File Docs|
|--|--|--|--|--|--|
|IPS|[`ipsluna.ips`](https://github.com/BrettefromNesUniverse/ipsluna/blob/main/src/ipsluna/ips/__init__.py)| [ipsluna.ips](https://github.com/BrettefromNesUniverse/ipsluna/blob/main/docs/ipsluna.ips_docs.md) |0.9|18.3 KB |None |
|BPS|[`ipsluna.bps`]()|Not yet|alpha|5.85 KB|None
|Xdelta|[`ipsluna.xdelta`]()|Not yet|None|None|None
|PPF|[`ipsluna.ppf`]()|Not yet|None|None|None
|UPS|[`ipsluna.ups`]()|Not yet|None|None|None
|APS|[`ipsluna.aps`]()|Not yet|None|None|None
|RUP|[`ipsluna.rup`]()|Not yet|None|None|None
|NPS|[`ipsluna.nps`]()|Not yet|None|None|None
|Luna|[`ipsluna.luna`]()|Not yet|None|None|None

Using `import ipsluna` will install all packages with the `importlib` module. `ipsluna` provides no context abundant methods and relies on the package being specified.

`Luna` serialized class handling may be implemented at a later point in time once enough of the crucial patch filetypes have been completed.
