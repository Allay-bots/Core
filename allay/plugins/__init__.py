
# Standard libs ---------------------------------------------------------------

import os

# Modules ---------------------------------------------------------------------

path = "allay/plugins"
all_modules: list[str] = []

for plugin in os.listdir(path):

    if not os.path.isdir(os.path.join(path,plugin)):
        continue
    if plugin.startswith("_"):
        continue

    all_modules.append(plugin)
