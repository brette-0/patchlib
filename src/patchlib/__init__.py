"""
Import all patchlib subpackages.
"""

from importlib import import_module
try:ips = import_module("patchlib.ips")
except: print("Missing `patchlib.ips`")
