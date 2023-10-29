
# Standard libs ---------------------------------------------------------------

import importlib
import os

# Modules ---------------------------------------------------------------------

path = "allay/builtins"
all = []

for plugin in os.listdir("allay/builtins"):
    if not os.path.isdir(plugin):
        continue
    if plugin.startswith("_"):
        continue

    all.append(plugin)
    importlib.import_module(f"..{plugin}")