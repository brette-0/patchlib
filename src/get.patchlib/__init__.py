"""
Import all patchlib subpackages.
"""
__version__ = "1.1"

from importlib import import_module
try:ips = import_module("get.patchlib.ips")
except: print("Missing `patchlib.ips`")
