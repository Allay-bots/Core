
# Standard libs ---------------------------------------------------------------

import importlib
import os

# Modules ---------------------------------------------------------------------

path = "allay/builtins"
all = []

for plugin in os.listdir(path):

    if not os.path.isdir(os.path.join(path, plugin)):
        continue
    if plugin.startswith("_"):
        continue

    all.append(plugin)